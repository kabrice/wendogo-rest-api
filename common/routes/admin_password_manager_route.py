# common/routes/admin_password_manager_route.py - Routes pour la gestion du mot de passe admin

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models.user import User
from common.models.admin_session import AdminSession
from common.models.security_log import SecurityLog
from common.models.admin_password_reset import AdminPasswordReset
from common.models import db
from datetime import datetime, timedelta
import secrets
import bcrypt
import jwt

def generate_secure_password(length=16):
    """Générer un mot de passe sécurisé lisible"""
    # Utiliser des caractères facilement lisibles
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%&*"
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password

def generate_access_token(email):
    """Générer un token d'accès temporaire pour Brice"""
    payload = {
        'email': email,
        'purpose': 'password_manager_access',
        'exp': datetime.utcnow() + timedelta(hours=2),  # Valide 2h
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_brice_access(email, token=None):
    """Vérifier que l'accès est autorisé pour Brice"""
    if email != 'briceouabo@gmail.com':
        return False
    
    if token:
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return (payload.get('email') == email and 
                    payload.get('purpose') == 'password_manager_access')
        except jwt.InvalidTokenError:
            return False
    
    return True  # Accès direct autorisé pour Brice

def send_password_email(password, action_type="generate"):
    """Envoyer le nouveau mot de passe à Brice"""
    try:
        from app import mail
        
        action_titles = {
            "generate": "Nouveau mot de passe admin généré",
            "reset": "Mot de passe admin réinitialisé", 
            "initial": "Mot de passe admin initial"
        }
        
        action_descriptions = {
            "generate": "Un nouveau mot de passe sécurisé a été généré",
            "reset": "Le mot de passe admin a été réinitialisé",
            "initial": "Le mot de passe admin initial a été configuré"
        }
        
        title = action_titles.get(action_type, "Nouveau mot de passe admin")
        description = action_descriptions.get(action_type, "Mot de passe mis à jour")
        
        email_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>🔐 {title} - Wendogo</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8fafc;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="margin: 0 0 10px 0; font-size: 28px;">🔐 Wendogo Admin</h1>
                <p style="margin: 0; opacity: 0.9; font-size: 16px;">{title}</p>
            </div>
            
            <!-- Content -->
            <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h2 style="color: #1e40af; margin: 0 0 10px 0;">{description}</h2>
                    <p style="color: #64748b; margin: 0;">Demande traitée le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                </div>
                
                <!-- Credentials Box -->
                <div style="background: #f1f5f9; padding: 25px; border-radius: 10px; margin: 25px 0; border: 2px solid #3b82f6;">
                    <h3 style="color: #1e40af; margin: 0 0 20px 0; text-align: center;">
                        🔑 Nouvelles informations de connexion
                    </h3>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0;">
                        <table style="width: 100%; font-family: 'Courier New', monospace;">
                            <tr>
                                <td style="padding: 8px 0; color: #475569; font-weight: bold;">URL Admin :</td>
                                <td style="padding: 8px 0; color: #1e293b;">http://localhost:3000/admin</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #475569; font-weight: bold;">Email :</td>
                                <td style="padding: 8px 0; color: #1e293b;">admin@wendogo.com</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px 0; color: #475569; font-weight: bold;">Mot de passe :</td>
                                <td style="padding: 8px 0;">
                                    <div style="background: #fef2f2; padding: 8px 12px; border-radius: 6px; border: 1px solid #fecaca;">
                                        <span style="color: #dc2626; font-weight: bold; font-size: 16px; letter-spacing: 1px;">{password}</span>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/admin" 
                       style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold; 
                              font-size: 16px;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                              display: inline-block;
                              margin-right: 15px;">
                        🚀 Accéder à l'admin
                    </a>
                    
                    <a href="http://localhost:3000/admin/password-manager?email=briceouabo@gmail.com" 
                       style="background: #f8fafc; 
                              color: #475569; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold; 
                              border: 2px solid #e2e8f0;
                              display: inline-block;">
                        ⚙️ Gérer les mots de passe
                    </a>
                </div>
                
                <!-- Security Warning -->
                <div style="background: #fef3cd; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 5px solid #f59e0b;">
                    <h3 style="color: #92400e; margin: 0 0 15px 0; display: flex; align-items: center; gap: 8px;">
                        ⚠️ Instructions de sécurité importantes
                    </h3>
                    <ul style="color: #92400e; margin: 0; padding-left: 20px; line-height: 1.6;">
                        <li><strong>Utilisez ce mot de passe immédiatement</strong> - Il peut être changé depuis l'interface admin</li>
                        <li><strong>Conservez ce mot de passe en sécurité</strong> - Ne le partagez jamais</li>
                        <li><strong>Supprimez cet email</strong> après avoir noté le mot de passe</li>
                        <li><strong>En cas de problème</strong> - Utilisez l'interface de gestion des mots de passe</li>
                    </ul>
                </div>
                
                <!-- Statistics -->
                <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #1e40af; margin: 0 0 15px 0;">📊 Informations techniques</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; color: #64748b; font-size: 14px;">
                        <div>🔐 Chiffrement : bcrypt avec salt</div>
                        <div>📏 Longueur : {len(password)} caractères</div>
                        <div>🔀 Entropie : Très élevée</div>
                        <div>⏰ Généré : {datetime.now().strftime('%H:%M:%S')}</div>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; margin-top: 25px; color: #94a3b8; font-size: 13px;">
                <p style="margin: 0 0 5px 0;">🤖 Email automatique généré par le système de sécurité Wendogo</p>
                <p style="margin: 0;">Cet email contient des informations sensibles - Traitez-le avec précaution</p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=f"🔐 {title} - Wendogo Admin",
            recipients=['briceouabo@gmail.com'],
            html=email_content
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

def send_access_link_email(email):
    """Envoyer un lien d'accès sécurisé à Brice"""
    try:
        from app import mail
        
        # Générer le token d'accès
        access_token = generate_access_token(email)
        access_url = f"http://localhost:3000/admin/password-manager?email={email}&token={access_token}"
        
        email_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>🔗 Accès Gestionnaire Mot de Passe - Wendogo</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8fafc;">
            <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="margin: 0 0 10px 0; font-size: 28px;">🔗 Accès Sécurisé</h1>
                <p style="margin: 0; opacity: 0.9;">Gestionnaire de Mot de Passe Admin</p>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #047857; text-align: center; margin: 0 0 20px 0;">
                    Lien d'accès généré
                </h2>
                
                <p style="color: #374151; text-align: center; margin-bottom: 25px;">
                    Cliquez sur le bouton ci-dessous pour accéder à l'interface de gestion des mots de passe admin.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{access_url}" 
                       style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                              color: white; 
                              padding: 18px 35px; 
                              text-decoration: none; 
                              border-radius: 10px; 
                              font-weight: bold; 
                              font-size: 18px;
                              box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                              display: inline-block;">
                        🔐 Accéder au gestionnaire
                    </a>
                </div>
                
                <div style="background: #fef3cd; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 5px solid #f59e0b;">
                    <h3 style="color: #92400e; margin: 0 0 10px 0;">⏰ Important</h3>
                    <p style="color: #92400e; margin: 0;">
                        Ce lien est valide pendant <strong>2 heures</strong> uniquement pour des raisons de sécurité.
                    </p>
                </div>
                
                <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #1e40af; margin: 0 0 15px 0;">🛡️ Avec cette interface, vous pouvez :</h3>
                    <ul style="color: #64748b; margin: 0; padding-left: 20px; line-height: 1.8;">
                        <li>Générer de nouveaux mots de passe sécurisés</li>
                        <li>Réinitialiser le mot de passe admin</li>
                        <li>Voir le statut du compte admin</li>
                        <li>Révoquer toutes les sessions admin actives</li>
                        <li>Consulter les logs de sécurité récents</li>
                    </ul>
                </div>
                
                <div style="border-top: 1px solid #e2e8f0; padding-top: 20px; margin-top: 30px;">
                    <p style="color: #64748b; font-size: 14px; text-align: center; margin: 0;">
                        Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                        <a href="{access_url}" style="color: #3b82f6; word-break: break-all;">{access_url}</a>
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 25px; color: #94a3b8; font-size: 13px;">
                <p style="margin: 0;">🔒 Lien sécurisé généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject="🔗 Accès Gestionnaire Mot de Passe Admin - Wendogo",
            recipients=[email],
            html=email_content
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi lien d'accès: {e}")
        return False

def log_password_action(action_type, email, additional_data=None):
    """Logger les actions de gestion de mot de passe"""
    try:
        log_entry = SecurityLog(
            event_type=f'password_manager_{action_type}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            additional_data={
                'requested_by': email,
                'action': action_type,
                **(additional_data or {})
            }
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Erreur logging: {e}")

def init_routes(app):
    
    @app.route('/api/admin/password-manager/request-access', methods=['POST'])
    def request_access():
        """Demander un accès au gestionnaire de mot de passe"""
        try:
            data = request.json
            email = data.get('email')
            
            if not verify_brice_access(email):
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
            
            # Envoyer le lien d'accès sécurisé
            if send_access_link_email(email):
                log_password_action('access_requested', email)
                return jsonify({'success': True, 'message': 'Lien d\'accès envoyé'})
            else:
                return jsonify({'success': False, 'error': 'Erreur envoi email'}), 500
                
        except Exception as e:
            print(f"❌ Erreur request_access: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/password-manager/verify-access', methods=['POST'])
    def verify_access():
        """Vérifier l'accès au gestionnaire"""
        try:
            data = request.json
            email = data.get('email')
            token = data.get('token')
            
            if verify_brice_access(email, token):
                log_password_action('access_verified', email)
                return jsonify({'success': True})
            else:
                log_password_action('access_denied', email, {'reason': 'invalid_token'})
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
                
        except Exception as e:
            print(f"❌ Erreur verify_access: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/password-manager/status', methods=['GET'])
    def get_admin_status():
        """Récupérer le statut du compte admin"""
        try:
            # Récupérer l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            
            if not admin_user:
                return jsonify({'success': False, 'error': 'Admin non trouvé'}), 404
            
            # Compter les sessions actives
            active_sessions = AdminSession.query.filter_by(
                user_id=admin_user.id,
                is_active=True
            ).filter(AdminSession.expires_at > datetime.utcnow()).count()
            
            # Récupérer les logs récents
            recent_logs = SecurityLog.query.filter(
                SecurityLog.event_type.like('admin_%')
            ).order_by(SecurityLog.timestamp.desc()).limit(20).all()
            
            return jsonify({
                'success': True,
                'admin': {
                    'id': admin_user.id,
                    'email': admin_user.email,
                    'last_login': admin_user.last_login.isoformat() if admin_user.last_login else None,
                    'has_password': bool(admin_user.password),
                    'active_sessions': active_sessions
                },
                'recentLogs': [log.as_dict() for log in recent_logs]
            })
            
        except Exception as e:
            print(f"❌ Erreur get_admin_status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/password-manager/generate', methods=['POST'])
    def generate_new_password():
        """Générer un nouveau mot de passe admin"""
        try:
            data = request.json
            email = data.get('requestedBy')
            
            if not verify_brice_access(email):
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
            
            # Récupérer l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            if not admin_user:
                return jsonify({'success': False, 'error': 'Admin non trouvé'}), 404
            
            # Générer le nouveau mot de passe
            new_password = generate_secure_password()
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Mettre à jour le mot de passe
            admin_user.password = password_hash
            db.session.commit()
            
            # Envoyer par email
            if send_password_email(new_password, "generate"):
                log_password_action('password_generated', email, {
                    'password_length': len(new_password)
                })
                return jsonify({
                    'success': True,
                    'password': new_password,
                    'message': 'Nouveau mot de passe généré et envoyé par email'
                })
            else:
                return jsonify({'success': False, 'error': 'Erreur envoi email'}), 500
                
        except Exception as e:
            print(f"❌ Erreur generate_new_password: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/password-manager/reset', methods=['POST'])
    def reset_admin_password():
        """Réinitialiser le mot de passe admin"""
        try:
            data = request.json
            email = data.get('requestedBy')
            
            if not verify_brice_access(email):
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
            
            # Récupérer l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            if not admin_user:
                return jsonify({'success': False, 'error': 'Admin non trouvé'}), 404
            
            # Générer un mot de passe de réinitialisation
            reset_password = generate_secure_password()
            password_hash = bcrypt.hashpw(reset_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Mettre à jour le mot de passe
            admin_user.password = password_hash
            
            # Révoquer toutes les sessions actives
            AdminSession.query.filter_by(
                user_id=admin_user.id,
                is_active=True
            ).update({'is_active': False, 'logged_out_at': datetime.utcnow()})
            
            db.session.commit()
            
            # Envoyer par email
            if send_password_email(reset_password, "reset"):
                log_password_action('password_reset', email, {
                    'sessions_revoked': True
                })
                return jsonify({
                    'success': True,
                    'password': reset_password,
                    'message': 'Mot de passe réinitialisé et toutes les sessions révoquées'
                })
            else:
                return jsonify({'success': False, 'error': 'Erreur envoi email'}), 500
                
        except Exception as e:
            print(f"❌ Erreur reset_admin_password: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/admin/password-manager/revoke-sessions', methods=['POST'])
    def revoke_admin_sessions():
        """Révoquer toutes les sessions admin actives"""
        try:
            data = request.json
            email = data.get('requestedBy')
            
            if not verify_brice_access(email):
                return jsonify({'success': False, 'error': 'Accès non autorisé'}), 403
            
            # Révoquer toutes les sessions admin actives
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            if not admin_user:
                return jsonify({'success': False, 'error': 'Admin non trouvé'}), 404
            
            revoked_count = AdminSession.query.filter_by(
                user_id=admin_user.id,
                is_active=True
            ).update({'is_active': False, 'logged_out_at': datetime.utcnow()})
            
            db.session.commit()
            
            log_password_action('sessions_revoked', email, {
                'revoked_count': revoked_count
            })
            
            return jsonify({
                'success': True,
                'message': f'{revoked_count} session(s) révoquée(s) avec succès'
            })
            
        except Exception as e:
            print(f"❌ Erreur revoke_admin_sessions: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
