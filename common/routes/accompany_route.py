# common/routes/accompany_route.py - Routes pour l'accompagnement

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models.user import User
from common.models.accompany_request import AccompanyRequest
from common.models.organization_contact import OrganizationContact
from common.models import db
from functools import wraps
from datetime import datetime
import jwt

def require_auth(f):
    """Décorateur pour vérifier l'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token format invalide'}), 401
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expiré'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token invalide'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def send_notification_email(subject, content, recipient=None):
    """Envoyer un email de notification"""
    try:
        from app import mail
        
        msg = Message(
            subject=subject,
            recipients=[recipient or 'hello@wendogo.com'],
            html=content
        )
        
        mail.send(msg)
        print(f"✅ Email envoyé à {recipient or 'hello@wendogo.com'}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi email: {e}")
        return False

def send_sms_notification(message, phone_number="+33755097584"):
    """Envoyer une notification SMS (optionnel)"""
    try:
        # Ici vous pouvez intégrer un service SMS gratuit ou peu cher
        # comme Twilio, SMS.to, ou utiliser une API gratuite
        
        # Pour l'instant, on log juste le message
        print(f"📱 SMS à envoyer à {phone_number}: {message}")
        
        # TODO: Intégrer un service SMS si budget disponible
        return True
    except Exception as e:
        print(f"❌ Erreur envoi SMS: {e}")
        return False

def init_routes(app):
    
    @app.route('/api/accompany/request', methods=['POST'])
    @require_auth
    def create_accompany_request(current_user):
        """Créer une demande d'accompagnement"""
        try:
            data = request.json
            
            # Validation des données
            required_fields = ['offerId', 'offerName', 'price', 'projectDescription']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'{field} requis'}), 400
            
            # Créer la demande d'accompagnement
            accompany_request = AccompanyRequest(
                user_id=current_user.id,
                offer_id=data['offerId'],
                offer_name=data['offerName'],
                price=data['price'],
                currency=data.get('currency', 'EUR'),
                project_description=data['projectDescription'],
                additional_info=data.get('additionalInfo', ''),
                preferred_contact=data.get('preferredContact', 'email'),
                urgency=data.get('urgency', 'normal'),
                status='pending'
            )
            
            db.session.add(accompany_request)
            db.session.commit()
            
            # Préparer le contenu de l'email de notification
            urgency_text = {
                'normal': 'Normal (24-48h)',
                'urgent': 'Urgent (24h)',
                'very_urgent': 'Très urgent (immédiat)'
            }.get(data.get('urgency', 'normal'), 'Normal')
            
            contact_text = {
                'whatsapp': 'WhatsApp',
                'email': 'Email',
                'phone': 'Téléphone'
            }.get(data.get('preferredContact', 'email'), 'Email')
            
            # Email de notification admin
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Nouvelle demande d'accompagnement - Wendogo</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🎯 Nouvelle demande d'accompagnement</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-top: 0;">Détails de la demande</h2>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h3 style="color: #667eea; margin-top: 0;">👤 Informations client</h3>
                        <p><strong>Nom :</strong> {current_user.firstname} {current_user.lastname}</p>
                        <p><strong>Email :</strong> {current_user.email}</p>
                        <p><strong>Téléphone :</strong> {current_user.phone or 'Non renseigné'}</p>
                        <p><strong>Pays :</strong> {current_user.country or 'Non renseigné'}</p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h3 style="color: #667eea; margin-top: 0;">📦 Offre sélectionnée</h3>
                        <p><strong>Pack :</strong> {data['offerName']}</p>
                        <p><strong>Prix :</strong> {data['price']}€ ({data.get('currency', 'EUR')})</p>
                        <p><strong>Urgence :</strong> {urgency_text}</p>
                        <p><strong>Contact préféré :</strong> {contact_text}</p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h3 style="color: #667eea; margin-top: 0;">📝 Projet étudiant</h3>
                        <p><strong>Description :</strong></p>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px;">
                            {data['projectDescription']}
                        </div>
                        
                        {f'''
                        <p style="margin-top: 15px;"><strong>Informations supplémentaires :</strong></p>
                        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px;">
                            {data.get('additionalInfo', 'Aucune')}
                        </div>
                        ''' if data.get('additionalInfo') else ''}
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3;">
                        <p style="margin: 0; color: #1565c0;">
                            <strong>🚀 Action requise :</strong> Contacter ce prospect sous {urgency_text.lower()} 
                            via {contact_text.lower()}.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:3000/admin/accompany-requests" 
                           style="background: #667eea; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Voir dans l'admin
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                    <p>© 2025 Wendogo - Système de notifications automatiques</p>
                </div>
            </body>
            </html>
            """
            
            # Envoyer l'email de notification
            send_notification_email(
                subject=f"🎯 Nouvelle demande d'accompagnement - {data['offerName']} ({urgency_text})",
                content=email_content
            )
            
            # Envoyer SMS si urgent
            if data.get('urgency') in ['urgent', 'very_urgent']:
                sms_message = f"🚨 WENDOGO: Nouvelle demande {data['offerName']} URGENTE de {current_user.firstname} {current_user.lastname}. Voir admin: http://localhost:3000/admin"
                send_sms_notification(sms_message)
            
            # Mettre à jour le dashboard utilisateur
            current_user.has_accompany_request = True
            current_user.last_accompany_request_id = accompany_request.id
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Demande envoyée avec succès',
                'request_id': accompany_request.id
            })
            
        except Exception as e:
            print(f"❌ Erreur create_accompany_request: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/organizations/contact', methods=['POST'])
    def create_organization_contact():
        """Créer un contact d'organisme"""
        try:
            data = request.json
            
            # Validation des données
            required_fields = ['firstName', 'lastName', 'position', 'organization', 'email', 'message']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'{field} requis'}), 400
            
            # Validation email
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data['email']):
                return jsonify({'success': False, 'error': 'Format email invalide'}), 400
            
            # Créer le contact d'organisme
            organization_contact = OrganizationContact(
                first_name=data['firstName'],
                last_name=data['lastName'],
                position=data['position'],
                organization=data['organization'],
                email=data['email'],
                message=data['message'],
                status='new'
            )
            
            db.session.add(organization_contact)
            db.session.commit()
            
            # Email de notification admin
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Nouveau contact d'organisme - Wendogo</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🏢 Nouveau contact d'organisme</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333; margin-top: 0;">Détails du contact</h2>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h3 style="color: #667eea; margin-top: 0;">👤 Informations de contact</h3>
                        <p><strong>Nom :</strong> {data['firstName']} {data['lastName']}</p>
                        <p><strong>Poste :</strong> {data['position']}</p>
                        <p><strong>Établissement :</strong> {data['organization']}</p>
                        <p><strong>Email :</strong> {data['email']}</p>
                    </div>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <h3 style="color: #667eea; margin-top: 0;">📝 Message</h3>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; line-height: 1.6;">
                            {data['message']}
                        </div>
                    </div>
                    
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; border-left: 4px solid #4caf50;">
                        <p style="margin: 0; color: #2e7d32;">
                            <strong>🤝 Opportunité de partenariat :</strong> Nouveau prospect à contacter rapidement.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://localhost:3000/admin/organization-contacts" 
                           style="background: #667eea; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; font-weight: bold;">
                            Voir dans l'admin
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                    <p>© 2025 Wendogo - Système de notifications automatiques</p>
                </div>
            </body>
            </html>
            """
            
            # Envoyer l'email de notification
            send_notification_email(
                subject=f"🏢 Nouveau contact: {data['organization']} - {data['firstName']} {data['lastName']}",
                content=email_content
            )
            
            # SMS pour les contacts importants
            sms_message = f"🏢 WENDOGO: Nouveau contact {data['organization']} - {data['firstName']} {data['lastName']} ({data['position']}). Voir admin."
            send_sms_notification(sms_message)
            
            return jsonify({
                'success': True,
                'message': 'Message envoyé avec succès'
            })
            
        except Exception as e:
            print(f"❌ Erreur create_organization_contact: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/accompany/requests', methods=['GET'])
    @require_auth  
    def get_user_accompany_requests(current_user):
        """Récupérer les demandes d'accompagnement de l'utilisateur"""
        try:
            requests = AccompanyRequest.query.filter_by(user_id=current_user.id).order_by(AccompanyRequest.created_at.desc()).all()
            
            return jsonify({
                'success': True,
                'requests': [req.as_dict() for req in requests]
            })
            
        except Exception as e:
            print(f"❌ Erreur get_user_accompany_requests: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
