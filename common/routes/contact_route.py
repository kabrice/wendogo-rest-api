# common/routes/contact_route.py - Version avec modèle SQLAlchemy

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models import db
from common.models.contact_message import ContactMessage
from datetime import datetime
import re

def init_routes(app):
    @app.route('/api/contact/send-message', methods=['POST'])
    def send_contact_message():
        try:
            # Récupérer les données du formulaire
            data = request.get_json()
            
            # Validation des données
            required_fields = ['name', 'email', 'subject', 'message', 'projectType']
            for field in required_fields:
                if not data.get(field) or not data[field].strip():
                    return jsonify({
                        'success': False,
                        'error': f'Le champ {field} est requis'
                    }), 400
            
            # Validation email
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, data['email']):
                return jsonify({
                    'success': False,
                    'error': 'Format email invalide'
                }), 400
            
            # Préparer les données nettoyées
            name = data['name'].strip()
            email = data['email'].strip()
            subject = data['subject'].strip()
            message_content = data['message'].strip()
            project_type = data['projectType'].strip()
            
            # ✅ CRÉER ET SAUVEGARDER LE MESSAGE AVEC LE MODÈLE
            try:
                contact_message = ContactMessage(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message_content,
                    project_type=project_type,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')
                )
                
                db.session.add(contact_message)
                db.session.commit()
                
                current_app.logger.info(f"Contact message saved with ID: {contact_message.id}")
                
            except Exception as db_error:
                current_app.logger.error(f"Error saving to database: {str(db_error)}")
                db.session.rollback()
                # Continuer même si la sauvegarde échoue - l'email reste prioritaire
                contact_message = None
            
            # Créer le message email pour l'équipe
            email_subject = f"[WENDOGO CONTACT] {subject}"
            
            project_emoji = {
                'orientation': '🎓',
                'visa': '📋',
                'campus-france': '🏛️',
                'parcoursup': '📚',
                'logement': '🏠',
                'general': '❓',
                'other': '📝'
            }.get(project_type, '📝')
            
            urgency_indicator = "🔥 URGENT" if project_type in ['visa', 'campus-france', 'parcoursup'] else "📧 NORMAL"
            
            email_body = f"""
{urgency_indicator} - NOUVEAU MESSAGE DE CONTACT

═══════════════════════════════════════════════════
📋 INFORMATIONS CONTACT
═══════════════════════════════════════════════════
👤 Nom : {name}
📧 Email : {email}
{project_emoji} Type : {project_type.upper()}
📝 Sujet : {subject}

═══════════════════════════════════════════════════
💬 MESSAGE CLIENT
═══════════════════════════════════════════════════
{message_content}

═══════════════════════════════════════════════════
🔧 MÉTADONNÉES TECHNIQUES
═══════════════════════════════════════════════════
🕒 Reçu le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
🌐 IP : {request.remote_addr}
💻 User-Agent : {request.headers.get('User-Agent', 'Non spécifié')[:100]}...
🆔 Message ID : {contact_message.id if contact_message else 'Non sauvegardé'}

═══════════════════════════════════════════════════
🚀 ACTIONS RECOMMANDÉES
═══════════════════════════════════════════════════
Type: {project_type} {project_emoji}

📋 RÉPONSE SUGGÉRÉE:
{get_response_template(project_type)}

⏱️ DÉLAI DE RÉPONSE RECOMMANDÉ:
{get_response_urgency(project_type)}

📊 ADMIN PANEL:
https://wendogo.com/admin (onglet Messages contact)

---
Envoyé automatiquement depuis wendogo.com
Système de notification Wendogo v2.0
"""
            
            # Envoyer l'email à l'équipe
            msg = Message(
                subject=email_subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=['hello@wendogo.com'],
                reply_to=email,
                body=email_body
            )
            
            from app import mail
            mail.send(msg)
            
            # Email de confirmation personnalisé
            confirmation_subject = "Votre message a bien été reçu - Wendogo 🎓"
            confirmation_body = get_confirmation_email(name, subject, project_type, message_content)
            
            confirmation_msg = Message(
                subject=confirmation_subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email],
                body=confirmation_body
            )
            
            mail.send(confirmation_msg)
            
            current_app.logger.info(f"Contact emails sent successfully for {email}")
            
            return jsonify({
                'success': True,
                'message': 'Votre message a été envoyé avec succès ! Nous vous répondrons rapidement.',
                'message_id': contact_message.id if contact_message else None
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error sending contact message: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'envoi du message. Veuillez réessayer ou nous contacter directement.'
            }), 500
    @app.route('/debug/env', methods=['GET'])
    def debug_env():
        import os
        return {
            'working_dir': os.getcwd(),
            'env_exists': os.path.exists('.env'),
            'mail_server': os.getenv('MAIL_SERVER'),
            'mail_username': os.getenv('MAIL_USERNAME'),
            'mail_default_sender': os.getenv('MAIL_DEFAULT_SENDER'),
            'flask_config_sender': app.config.get('MAIL_DEFAULT_SENDER')
        }
    @app.route('/api/contact/test-email', methods=['POST'])
    def test_email_config():
        """Route de test pour vérifier la configuration email"""
        try:
            from app import mail
            
            msg = Message(
                subject="✅ Test Configuration Email Wendogo",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=['hello@wendogo.com'],
                body=f"""
🧪 TEST DE CONFIGURATION EMAIL

✅ Configuration SMTP : FONCTIONNELLE
📧 Serveur : {current_app.config['MAIL_SERVER']}
🔐 Port : {current_app.config['MAIL_PORT']}
👤 Expéditeur : {current_app.config['MAIL_DEFAULT_SENDER']}

📊 Statistiques des messages :
{ContactMessage.get_stats() if 'ContactMessage' in globals() else 'Modèle non disponible'}

🕒 Date du test : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
🏗️ Environnement : {current_app.config.get('ENV', 'Unknown')}

Si vous recevez ce message, la configuration email fonctionne parfaitement !
"""
            )
            
            mail.send(msg)
            
            return jsonify({
                'success': True,
                'message': 'Email de test envoyé avec succès',
                'timestamp': datetime.now().isoformat()
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Error testing email: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Erreur email : {str(e)}'
            }), 500

def get_response_template(project_type):
    """Retourne un template de réponse selon le type de projet"""
    templates = {
        'orientation': """
• Proposer un appel découverte gratuit (15 min)
• Envoyer le lien vers le simulateur
• Mentionner nos 2100+ formations référencées
• Proposer l'accompagnement personnalisé""",
        
        'visa': """
• Envoyer le guide visa étudiant complet
• Vérifier l'éligibilité Campus France
• Proposer l'accompagnement visa premium
• Planifier un appel pour évaluer le dossier""",
        
        'campus-france': """
• Expliquer la procédure selon le pays
• Vérifier les documents requis
• Proposer l'accompagnement Campus France
• Donner les délais de traitement""",
        
        'parcoursup': """
• Clarifier l'éligibilité pour étudiants étrangers
• Expliquer les formations accessibles (BTS, CPGE, DCG)
• Proposer l'accompagnement spécialisé""",
        
        'logement': """
• Envoyer le guide logement étudiant
• Proposer nos partenaires logement
• Conseils pour les garanties""",
        
        'default': """
• Réponse personnalisée selon la demande
• Proposer un appel découverte
• Rediriger vers les ressources pertinentes"""
    }
    return templates.get(project_type, templates['default'])

def get_response_urgency(project_type):
    """Retourne l'urgence de réponse selon le type"""
    if project_type in ['visa', 'campus-france']:
        return "⚡ URGENT - Répondre sous 1h (délais serrés)"
    elif project_type in ['parcoursup']:
        return "🔥 PRIORITAIRE - Répondre sous 2h"
    else:
        return "📧 STANDARD - Répondre sous 24h"

def get_confirmation_email(name, subject, project_type, message_content):
    """Génère l'email de confirmation personnalisé"""
    
    project_info = {
        'orientation': {
            'emoji': '🎓',
            'title': 'votre recherche d\'orientation',
            'next_steps': """
🎯 PROCHAINES ÉTAPES POUR VOTRE ORIENTATION :

1. 📊 Faites vous accomagner
   → https://wendogo.com/?tab=accompany#accompany-section

2. 📞 Réservez votre appel découverte (15 min gratuit)
   → Un expert analyse votre profil

3. 🎓 Recevez vos recommandations personnalisées
   → Parmi nos 2100+ formations référencées

💡 CONSEIL : Commencez par notre simulateur pour une première évaluation !"""
        },
        
        'visa': {
            'emoji': '📋',
            'title': 'votre demande de visa étudiant',
            'next_steps': """
📋 PROCHAINES ÉTAPES POUR VOTRE VISA :

1. 📖 Consultez notre guide complet
   → https://wendogo.com/guides/etudier-en-france

2. ✅ Vérifiez votre éligibilité Campus France
   → Selon votre pays de résidence

3. 🎯 Maximisez vos chances avec notre accompagnement
   → Préparation complète du dossier

⚠️ IMPORTANT : Les délais de visa peuvent être longs, commencez tôt !"""
        },
        
        'campus-france': {
            'emoji': '🏛️',
            'title': 'la procédure Campus France',
            'next_steps': """
🏛️ AIDE CAMPUS FRANCE :

1. 🌍 Vérifiez si votre pays est concerné
   → Liste complète dans notre guide

2. 📋 Préparez votre dossier étape par étape
   → Documents, délais, entretien

3. 🎯 Bénéficiez de notre expertise
   → Accompagnement spécialisé Campus France

📅 DÉLAIS : Commencez 6-8 mois avant votre rentrée !"""
        },
        
        'default': {
            'emoji': '💼',
            'title': 'votre projet d\'études en France',
            'next_steps': """
🚀 RESSOURCES UTILES POUR VOTRE PROJET :

• 📖 Guides complets : wendogo.com/guides/etudier-en-france
• 🔍 Recherche formations : wendogo.com
• 📊 Faites vous accompanger : wendogo.com/?tab=accompany#accompany-section
• 💬 Support immédiat : WhatsApp +33 6 68 15 60 73"""
        }
    }
    
    info = project_info.get(project_type, project_info['default'])
    
    return f"""
Bonjour {name} ! 👋

Merci pour votre message {info['emoji']} {info['title']}.

✅ CONFIRMATION DE RÉCEPTION
Nous avons bien reçu votre demande : "{subject}"

Notre équipe d'experts va analyser votre situation et vous répondre personnellement dans les plus brefs délais (généralement sous 2h en journée).

{info['next_steps']}

═══════════════════════════════════════════════════
🚀 BESOIN D'UNE RÉPONSE IMMÉDIATE ?
═══════════════════════════════════════════════════

📧 Email : hello@wendogo.com
📱 WhatsApp : +33 6 68 15 60 73 (réponse immédiate)
💬 Messenger : https://m.me/wendogoHQ
🌐 Site web : https://wendogo.com

═══════════════════════════════════════════════════
📋 RÉCAPITULATIF DE VOTRE DEMANDE
═══════════════════════════════════════════════════
Type de projet : {project_type} {info['emoji']}
Sujet : {subject}
Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}

Votre message :
{message_content}

═══════════════════════════════════════════════════

À très bientôt pour concrétiser votre projet d'études en France ! 🇫🇷

L'équipe Wendogo 🎓

P.S. : Ajoutez hello@wendogo.com à vos contacts pour ne manquer aucune de nos réponses !
"""
