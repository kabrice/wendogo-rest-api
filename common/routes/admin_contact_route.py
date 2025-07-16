# common/routes/admin_contact_route.py - Version avec modèle SQLAlchemy

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models import db
from common.models.user import User
from common.models.admin_session import AdminSession
from common.models.contact_message import ContactMessage
from common.models.security_log import SecurityLog
from datetime import datetime
from functools import wraps
import jwt
import bcrypt
import logging
from sqlalchemy import desc

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

def init_routes(app):


    @app.route('/api/admin/contact-messages', methods=['GET'])
    @require_admin_auth
    def get_contact_messages(admin_user):
        """Récupérer tous les messages de contact pour l'admin"""
        try:
            # Paramètres de filtrage
            status_filter = request.args.get('status', 'all')
            project_type_filter = request.args.get('project_type', 'all')
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Construire la requête
            query = ContactMessage.query
            
            if status_filter != 'all':
                query = query.filter(ContactMessage.status == status_filter)
            
            if project_type_filter != 'all':
                query = query.filter(ContactMessage.project_type == project_type_filter)
            
            # ✅ CORRIGÉ : Tri simple sans case() complexe
            # Nouveaux messages en premier, puis par date décroissante
            messages = query.order_by(
                ContactMessage.status == 'new',  # True (1) en premier
                desc(ContactMessage.created_at)
            ).offset(offset).limit(limit).all()
            
            # Convertir en dictionnaires
            messages_data = [message.as_dict() for message in messages]
            
            # Statistiques simples
            total_count = ContactMessage.query.count()
            filtered_count = query.count()
            new_count = ContactMessage.query.filter(ContactMessage.status == 'new').count()
            
            return jsonify({
                'success': True,
                'messages': messages_data,
                'total': total_count,
                'filtered_count': filtered_count,
                'new_count': new_count
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error fetching contact messages: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors du chargement des messages'
            }), 500

    @app.route('/api/admin/contact-messages/<int:message_id>', methods=['GET'])
    @require_admin_auth
    def get_contact_message(message_id):
        """Récupérer un message spécifique"""
        try:
            message = ContactMessage.query.get_or_404(message_id)
            return jsonify({
                'success': True,
                'message': message.as_dict()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error fetching message {message_id}: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Message non trouvé'
            }), 404

    @app.route('/api/admin/contact-messages/<int:message_id>/read', methods=['PATCH'])
    @require_admin_auth
    def mark_message_as_read(message_id):
        """Marquer un message comme lu"""
        try:
            message = ContactMessage.query.get_or_404(message_id)
            
            # Récupérer l'admin depuis le token (vous devrez adapter selon votre système d'auth)
            admin_email = request.current_user.get('email', 'admin@wendogo.com') if hasattr(request, 'current_user') else 'admin@wendogo.com'
            
            if message.status == 'new':
                message.mark_as_read(admin_email)
                
            return jsonify({
                'success': True,
                'message': 'Message marqué comme lu',
                'data': message.as_dict()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error marking message as read: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la mise à jour'
            }), 500

    @app.route('/api/admin/contact-messages/<int:message_id>/reply', methods=['POST'])
    @require_admin_auth
    def reply_to_message(message_id):
        """Répondre à un message de contact"""
        try:
            data = request.get_json()
            reply_text = data.get('reply', '').strip()
            
            if not reply_text:
                return jsonify({
                    'success': False,
                    'error': 'Le contenu de la réponse est requis'
                }), 400
            
            message = ContactMessage.query.get_or_404(message_id)
            admin_email = request.current_user.get('email', 'admin@wendogo.com') if hasattr(request, 'current_user') else 'admin@wendogo.com'
            
            # Préparer l'email de réponse
            email_subject = f"Re: {message.subject}"
            
            email_body = f"""{reply_text}

---
Cordialement,
L'équipe Wendogo 🎓

📧 hello@wendogo.com
📱 WhatsApp: +33 6 68 15 60 73
🌐 https://wendogo.com

---
VOTRE MESSAGE ORIGINAL :
Envoyé le : {message.created_at.strftime('%d/%m/%Y à %H:%M')}
Sujet : {message.subject}

{message.message}
"""
            
            # Envoyer l'email
            msg = Message(
                subject=email_subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[message.email],
                body=email_body
            )
            
            from app import mail
            mail.send(msg)
            
            # Marquer comme répondu avec note
            message.mark_as_replied(
                admin_email=admin_email,
                add_note=f"Réponse envoyée: {reply_text[:100]}..."
            )
            
            current_app.logger.info(f"Reply sent to {message.email} for message {message_id} by {admin_email}")
            
            return jsonify({
                'success': True,
                'message': 'Réponse envoyée avec succès',
                'data': message.as_dict()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error sending reply: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'envoi de la réponse'
            }), 500

    @app.route('/api/admin/contact-messages/<int:message_id>/archive', methods=['PATCH'])
    @require_admin_auth
    def archive_message(message_id):
        """Archiver un message"""
        try:
            data = request.get_json()
            reason = data.get('reason', 'Archivé via l\'interface admin')
            
            message = ContactMessage.query.get_or_404(message_id)
            admin_email = request.current_user.get('email', 'admin@wendogo.com') if hasattr(request, 'current_user') else 'admin@wendogo.com'
            
            message.archive(admin_email=admin_email, reason=reason)
            
            return jsonify({
                'success': True,
                'message': 'Message archivé avec succès',
                'data': message.as_dict()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error archiving message: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'archivage'
            }), 500

    @app.route('/api/admin/contact-messages/<int:message_id>/notes', methods=['POST'])
    @require_admin_auth
    def add_message_note(message_id):
        """Ajouter une note à un message"""
        try:
            data = request.get_json()
            note = data.get('note', '').strip()
            
            if not note:
                return jsonify({
                    'success': False,
                    'error': 'La note ne peut pas être vide'
                }), 400
            
            message = ContactMessage.query.get_or_404(message_id)
            admin_email = request.current_user.get('email', 'admin@wendogo.com') if hasattr(request, 'current_user') else 'admin@wendogo.com'
            
            message.add_admin_note(admin_email, note)
            
            return jsonify({
                'success': True,
                'message': 'Note ajoutée avec succès',
                'data': message.as_dict()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error adding note: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'ajout de la note'
            }), 500

    @app.route('/api/admin/contact-stats', methods=['GET'])
    @require_admin_auth
    def get_contact_stats():
        """Récupérer les statistiques des messages de contact"""
        try:
            # Statistiques globales
            global_stats = ContactMessage.get_stats()
            
            # Répartition par type de projet
            project_breakdown = ContactMessage.get_project_type_breakdown()
            
            # Messages récents
            recent_messages = [msg.as_dict() for msg in ContactMessage.get_recent_messages(5)]
            
            # Statistiques de réponse
            avg_response_time = db.session.query(
                db.func.avg(
                    db.func.timestampdiff(
                        db.text('HOUR'),
                        ContactMessage.created_at,
                        ContactMessage.replied_at
                    )
                )
            ).filter(
                ContactMessage.replied_at.isnot(None)
            ).scalar()
            
            return jsonify({
                'success': True,
                'stats': {
                    **global_stats,
                    'project_breakdown': project_breakdown,
                    'recent_messages': recent_messages,
                    'avg_response_time_hours': round(avg_response_time or 0, 1),
                    'unread_count': ContactMessage.get_unread_count()
                }
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error fetching contact stats: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors du chargement des statistiques'
            }), 500

    @app.route('/api/admin/contact-messages/bulk-action', methods=['POST'])
    @require_admin_auth
    def bulk_action_messages():
        """Actions en lot sur les messages"""
        try:
            data = request.get_json()
            action = data.get('action')
            message_ids = data.get('message_ids', [])
            
            if not action or not message_ids:
                return jsonify({
                    'success': False,
                    'error': 'Action et IDs de messages requis'
                }), 400
            
            messages = ContactMessage.query.filter(ContactMessage.id.in_(message_ids)).all()
            admin_email = request.current_user.get('email', 'admin@wendogo.com') if hasattr(request, 'current_user') else 'admin@wendogo.com'
            
            updated_count = 0
            
            for message in messages:
                if action == 'mark_read' and message.status == 'new':
                    message.mark_as_read(admin_email)
                    updated_count += 1
                elif action == 'archive':
                    message.archive(admin_email, "Action en lot via interface admin")
                    updated_count += 1
            
            return jsonify({
                'success': True,
                'message': f'{updated_count} messages mis à jour',
                'updated_count': updated_count
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error in bulk action: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'action en lot'
            }), 500

    @app.route('/api/admin/contact-messages/export', methods=['GET'])
    @require_admin_auth
    def export_messages():
        """Exporter les messages en CSV"""
        try:
            import csv
            from io import StringIO
            from flask import make_response
            
            # Filtres optionnels
            status_filter = request.args.get('status', 'all')
            project_type_filter = request.args.get('project_type', 'all')
            
            query = ContactMessage.query
            
            if status_filter != 'all':
                query = query.filter(ContactMessage.status == status_filter)
            
            if project_type_filter != 'all':
                query = query.filter(ContactMessage.project_type == project_type_filter)
            
            messages = query.order_by(ContactMessage.created_at.desc()).all()
            
            # Créer le CSV
            output = StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                'ID', 'Date', 'Nom', 'Email', 'Sujet', 'Type de projet',
                'Statut', 'Message', 'Assigné à', 'Date de réponse', 'Notes admin'
            ])
            
            # Données
            for message in messages:
                writer.writerow([
                    message.id,
                    message.created_at.strftime('%d/%m/%Y %H:%M') if message.created_at else '',
                    message.name,
                    message.email,
                    message.subject,
                    message.get_project_type_label(),
                    message.get_status_label(),
                    message.message[:200] + '...' if len(message.message) > 200 else message.message,
                    message.assigned_to or '',
                    message.replied_at.strftime('%d/%m/%Y %H:%M') if message.replied_at else '',
                    message.admin_notes or ''
                ])
            
            output.seek(0)
            
            # Créer la réponse
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=wendogo_messages_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"Error exporting messages: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'export'
            }), 500
