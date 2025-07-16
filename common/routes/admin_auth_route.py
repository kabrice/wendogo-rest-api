# common/routes/admin_auth_route.py - Authentification admin sécurisée

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models.user import User
from common.models.admin_session import AdminSession
from common.models.security_log import SecurityLog
from common.models import db
from functools import wraps
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
import logging

# Configuration du logging de sécurité
security_logger = logging.getLogger('wendogo.security')

def require_admin_auth(f):
    """Décorateur pour vérifier l'authentification admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                log_security_event('invalid_token_format', request.remote_addr)
                return jsonify({'error': 'Token format invalide'}), 401
        
        if not token:
            log_security_event('missing_token', request.remote_addr)
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Vérifier que c'est un token admin
            if data.get('role') != 'admin':
                log_security_event('invalid_role', request.remote_addr, {'user_id': data.get('user_id')})
                return jsonify({'error': 'Accès non autorisé'}), 403
            
            # Vérifier l'utilisateur
            admin_user = User.query.get(data['user_id'])
            if not admin_user or admin_user.email != 'admin@wendogo.com':
                log_security_event('invalid_admin_user', request.remote_addr, {'user_id': data.get('user_id')})
                return jsonify({'error': 'Utilisateur admin non valide'}), 401
            
            # Vérifier la session active
            session = AdminSession.query.filter_by(
                token_id=data.get('session_id'),
                is_active=True
            ).first()
            
            if not session or session.expires_at < datetime.utcnow():
                log_security_event('expired_session', request.remote_addr, {'user_id': admin_user.id})
                return jsonify({'error': 'Session expirée'}), 401
            
            # Mettre à jour la dernière activité
            session.last_activity = datetime.utcnow()
            db.session.commit()
            
        except jwt.ExpiredSignatureError:
            log_security_event('token_expired', request.remote_addr)
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            log_security_event('invalid_token', request.remote_addr)
            return jsonify({'error': 'Token invalide'}), 401
        
        return f(admin_user, *args, **kwargs)
    
    return decorated

def log_security_event(event_type, ip_address, additional_data=None):
    """Enregistrer un événement de sécurité"""
    try:
        log_entry = SecurityLog(
            event_type=event_type,
            ip_address=ip_address,
            user_agent=request.headers.get('User-Agent', ''),
            additional_data=additional_data or {},
            timestamp=datetime.utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
        
        # Log aussi dans le fichier de sécurité
        security_logger.warning(f"Security Event: {event_type} from {ip_address} - {additional_data}")
        
    except Exception as e:
        print(f"Erreur logging sécurité: {e}")

def send_security_alert(alert_type, details):
    """Envoyer une alerte de sécurité à Brice"""
    try:
        from app import mail
        
        # Template d'alerte sécurisé
        alert_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>🚨 ALERTE SÉCURITÉ - Wendogo Admin</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">🚨 ALERTE SÉCURITÉ</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Wendogo Admin Dashboard</p>
            </div>
            
            <div style="background: #fef2f2; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #fecaca;">
                <h2 style="color: #dc2626; margin-top: 0;">Type d'alerte : {alert_type}</h2>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #dc2626;">
                    <h3 style="color: #dc2626; margin-top: 0;">Détails de l'incident</h3>
                    <ul style="color: #374151; margin: 0; padding-left: 20px;">
                        <li><strong>Heure :</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)</li>
                        <li><strong>IP :</strong> {details.get('ip', 'Inconnue')}</li>
                        <li><strong>Email tenté :</strong> {details.get('email', 'N/A')}</li>
                        <li><strong>Tentatives :</strong> {details.get('attempts', 'N/A')}</li>
                        <li><strong>User-Agent :</strong> {details.get('user_agent', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="color: #374151; margin-top: 0;">Actions recommandées</h3>
                    <ul style="color: #6b7280; margin: 0; padding-left: 20px;">
                        <li>Vérifier les logs de sécurité complets</li>
                        <li>Changer le mot de passe admin si nécessaire</li>
                        <li>Bloquer l'IP si tentatives persistantes</li>
                        <li>Vérifier l'intégrité du système</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="http://localhost:3000/admin" 
                       style="background: #dc2626; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Accéder à l'admin
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                <p>⚠️ Ceci est une alerte automatique du système de sécurité Wendogo</p>
                <p>Ne pas répondre à cet email - Contactez l'équipe technique si nécessaire</p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=f"🚨 ALERTE SÉCURITÉ - {alert_type}",
            recipients=['briceouabo@gmail.com'],
            html=alert_content
        )
        
        mail.send(msg)
        print(f"✅ Alerte sécurité envoyée à Brice: {alert_type}")
        
    except Exception as e:
        print(f"❌ Erreur envoi alerte sécurité: {e}")

def generate_admin_password():
    """Générer un mot de passe sécurisé pour l'admin"""
    # Générer un mot de passe de 16 caractères avec lettres, chiffres et symboles
    password = secrets.token_urlsafe(12)  # Base64 URL-safe
    return password

def init_routes(app):
    
    @app.route('/api/admin/auth/login', methods=['POST'])
    def admin_login():
        """Connexion admin ultra-sécurisée"""
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            
            # Validation stricte de l'email
            if email != 'admin@wendogo.com':
                log_security_event('unauthorized_admin_attempt', ip_address, {
                    'attempted_email': email,
                    'user_agent': user_agent
                })
                
                # Envoyer alerte immédiate pour tentative non autorisée
                send_security_alert('Tentative d\'accès non autorisée', {
                    'ip': ip_address,
                    'email': email,
                    'user_agent': user_agent
                })
                
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
            
            # Récupérer l'utilisateur admin (ID = 1)
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            
            if not admin_user:
                log_security_event('admin_user_not_found', ip_address)
                return jsonify({'success': False, 'error': 'Utilisateur admin non trouvé'}), 404
            
            # Vérifier le mot de passe
            if not admin_user.password:
                log_security_event('admin_no_password', ip_address)
                return jsonify({'success': False, 'error': 'Mot de passe non configuré'}), 500
            
            # Vérification bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), admin_user.password.encode('utf-8')):
                log_security_event('admin_invalid_password', ip_address, {
                    'email': email,
                    'user_agent': user_agent
                })
                return jsonify({'success': False, 'error': 'Mot de passe incorrect'}), 401
            
            # Générer une session sécurisée
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=8)  # Session de 8h
            
            # Créer la session admin
            admin_session = AdminSession(
                user_id=admin_user.id,
                token_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            )
            
            db.session.add(admin_session)
            
            # Mettre à jour la dernière connexion
            admin_user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Générer le JWT token
            token_payload = {
                'user_id': admin_user.id,
                'email': admin_user.email,
                'role': 'admin',
                'session_id': session_id,
                'exp': expires_at
            }
            
            token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
            
            # Log de connexion réussie
            log_security_event('admin_login_success', ip_address, {
                'user_id': admin_user.id,
                'session_id': session_id
            })
            
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': admin_user.id,
                    'email': admin_user.email,
                    'firstname': admin_user.firstname,
                    'lastname': admin_user.lastname
                },
                'expires_at': expires_at.isoformat()
            })
            
        except Exception as e:
            log_security_event('admin_login_error', ip_address, {'error': str(e)})
            print(f"❌ Erreur admin_login: {e}")
            return jsonify({'success': False, 'error': 'Erreur serveur'}), 500

    @app.route('/api/admin/auth/verify', methods=['GET'])
    @require_admin_auth
    def verify_admin_token(admin_user):
        """Vérifier la validité du token admin"""
        return jsonify({
            'success': True,
            'user': {
                'id': admin_user.id,
                'email': admin_user.email,
                'firstname': admin_user.firstname,
                'lastname': admin_user.lastname
            }
        })

    @app.route('/api/admin/auth/logout', methods=['POST'])
    @require_admin_auth
    def admin_logout(admin_user):
        """Déconnexion admin sécurisée"""
        try:
            # Invalider toutes les sessions actives de cet admin
            AdminSession.query.filter_by(
                user_id=admin_user.id,
                is_active=True
            ).update({'is_active': False, 'logged_out_at': datetime.utcnow()})
            
            db.session.commit()
            
            log_security_event('admin_logout', request.remote_addr, {
                'user_id': admin_user.id
            })
            
            return jsonify({'success': True, 'message': 'Déconnexion réussie'})
            
        except Exception as e:
            print(f"❌ Erreur admin_logout: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/auth/request-reset', methods=['POST'])
    def request_admin_password_reset():
        """Demander une réinitialisation du mot de passe admin"""
        try:
            data = request.json
            target_email = data.get('email')  # briceouabo@gmail.com
            
            if target_email != 'briceouabo@gmail.com':
                return jsonify({'success': False, 'error': 'Email non autorisé'}), 403
            
            # Générer un nouveau mot de passe temporaire
            new_password = generate_admin_password()
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Mettre à jour le mot de passe de l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            if admin_user:
                admin_user.password = password_hash
                db.session.commit()
            
            # Envoyer le nouveau mot de passe à Brice
            reset_email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>🔑 Nouveau mot de passe Admin - Wendogo</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🔑 Nouveau Mot de Passe Admin</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">Wendogo - Accès Administrateur</p>
                </div>
                
                <div style="background: #f0fdf4; padding: 20px; border-radius: 0 0 10px 10px; border: 1px solid #bbf7d0;">
                    <h2 style="color: #047857; margin-top: 0;">Nouveau mot de passe généré</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #059669;">
                        <h3 style="color: #047857; margin-top: 0;">🔐 Informations de connexion</h3>
                        <div style="background: #f9fafb; padding: 15px; border-radius: 5px; font-family: monospace;">
                            <p style="margin: 0;"><strong>Email :</strong> admin@wendogo.com</p>
                            <p style="margin: 10px 0 0 0;"><strong>Mot de passe :</strong> <span style="background: #fee2e2; padding: 2px 6px; border-radius: 3px; color: #dc2626;">{new_password}</span></p>
                        </div>
                    </div>
                    
                    <div style="background: #fef3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                        <h3 style="color: #92400e; margin-top: 0;">⚠️ Instructions de sécurité</h3>
                        <ul style="color: #92400e; margin: 0; padding-left: 20px;">
                            <li>Ce mot de passe est temporaire et sécurisé</li>
                            <li>Changez-le immédiatement après connexion</li>
                            <li>Ne le partagez avec personne</li>
                            <li>Supprimez cet email après utilisation</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:3000/admin" 
                           style="background: #059669; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Accéder à l'administration
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                    <p>🔒 Email sécurisé généré automatiquement</p>
                    <p>Demande initiée le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
            
            from app import mail
            msg = Message(
                subject="🔑 Nouveau mot de passe Admin Wendogo",
                recipients=[target_email],
                html=reset_email_content
            )
            
            mail.send(msg)
            
            log_security_event('admin_password_reset_requested', request.remote_addr, {
                'target_email': target_email
            })
            
            return jsonify({'success': True, 'message': 'Nouveau mot de passe envoyé'})
            
        except Exception as e:
            print(f"❌ Erreur password reset: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/auth/security-alert', methods=['POST'])
    def handle_security_alert():
        """Gérer les alertes de sécurité"""
        try:
            data = request.json
            alert_type = data.get('type')
            
            if alert_type == 'failed_login_attempts':
                send_security_alert('Tentatives de connexion échouées', {
                    'ip': data.get('ip'),
                    'email': data.get('email'),
                    'attempts': data.get('attempts'),
                    'user_agent': request.headers.get('User-Agent', '')
                })
            
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"❌ Erreur security alert: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # Sécuriser toutes les routes admin existantes
    @app.route('/api/admin/accompany-requests', methods=['GET'])
    @require_admin_auth
    def get_admin_accompany_requests_secure(admin_user):
        """Version sécurisée de get_admin_accompany_requests"""
        from common.models.accompany_request import AccompanyRequest
        
        try:
            requests = (AccompanyRequest.query
                       .join(User, AccompanyRequest.user_id == User.id)
                       .order_by(AccompanyRequest.created_at.desc())
                       .all())
            
            requests_data = []
            for request in requests:
                request_dict = request.as_dict()
                request_dict['user'] = {
                    'id': request.user.id,
                    'firstname': request.user.firstname,
                    'lastname': request.user.lastname,
                    'email': request.user.email,
                    'phone': request.user.phone,
                    'country': request.user.country
                }
                requests_data.append(request_dict)
            
            return jsonify({
                'success': True,
                'requests': requests_data
            })
            
        except Exception as e:
            print(f"❌ Erreur get_admin_accompany_requests: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/organization-contacts', methods=['GET'])
    @require_admin_auth
    def get_admin_organization_contacts_secure(admin_user):
        """Version sécurisée de get_admin_organization_contacts"""
        from common.models.organization_contact import OrganizationContact
        
        try:
            contacts = (OrganizationContact.query
                       .order_by(OrganizationContact.created_at.desc())
                       .all())
            
            return jsonify({
                'success': True,
                'contacts': [contact.as_dict() for contact in contacts]
            })
            
        except Exception as e:
            print(f"❌ Erreur get_admin_organization_contacts: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/accompany-requests/<int:request_id>', methods=['PATCH'])
    @require_admin_auth
    def update_accompany_request_status_secure(admin_user, request_id):
        """Version sécurisée de update_accompany_request_status"""
        from common.models.accompany_request import AccompanyRequest
        
        try:
            data = request.json
            new_status = data.get('status')
            
            if not new_status:
                return jsonify({'success': False, 'error': 'Statut requis'}), 400
            
            accompany_request = AccompanyRequest.query.get_or_404(request_id)
            accompany_request.status = new_status
            
            if new_status == 'contacted' and not accompany_request.contacted_at:
                accompany_request.contacted_at = db.func.current_timestamp()
            
            user = User.query.get(accompany_request.user_id)
            if user:
                user.accompany_status = new_status
            
            db.session.commit()
            
            # Log de l'action admin
            log_security_event('admin_status_update', request.remote_addr, {
                'admin_id': admin_user.id,
                'request_id': request_id,
                'new_status': new_status
            })
            
            return jsonify({
                'success': True,
                'message': 'Statut mis à jour avec succès'
            })
            
        except Exception as e:
            print(f"❌ Erreur update_accompany_request_status: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
