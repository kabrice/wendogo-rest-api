# common/routes/contact_route.py - Version avec modèle SQLAlchemy et support bilingue (FR/EN)

from flask import request, jsonify, current_app
from flask_mail import Message
from common.models import db
from common.models.contact_message import ContactMessage
from datetime import datetime
from common.utils.i18n_helpers import get_locale_from_request
import re
import os
import logging

def get_response_template(project_type, locale='fr'):
    """Retourne un template de réponse selon le type de projet et la langue"""
    
    if locale == 'en':
        templates = {
            'orientation': """
• Offer a free discovery call (15 min)
• Send the link to the simulator
• Mention our 2100+ referenced programs
• Offer personalized support""",
            
            'visa': """
• Send the complete student visa guide
• Check Campus France eligibility
• Offer premium visa support
• Schedule a call to evaluate the application""",
            
            'campus-france': """
• Explain the procedure by country
• Check required documents
• Offer Campus France support
• Provide processing times""",
            
            'parcoursup': """
• Clarify eligibility for international students
• Explain accessible programs (BTS, CPGE, DCG)
• Offer specialized support""",
            
            'logement': """
• Send the student housing guide
• Offer our housing partners
• Advice on guarantees""",
            
            'default': """
• Personalized response according to the request
• Offer a discovery call
• Redirect to relevant resources"""
        }
    else:
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

def get_response_urgency(project_type, locale='fr'):
    """Retourne l'urgence de réponse selon le type et la langue"""
    if locale == 'en':
        if project_type in ['visa', 'campus-france']:
            return "⚡ URGENT - Reply within 1h (tight deadlines)"
        elif project_type in ['parcoursup']:
            return "🔥 PRIORITY - Reply within 2h"
        else:
            return "📧 STANDARD - Reply within 24h"
    else:
        if project_type in ['visa', 'campus-france']:
            return "⚡ URGENT - Répondre sous 1h (délais serrés)"
        elif project_type in ['parcoursup']:
            return "🔥 PRIORITAIRE - Répondre sous 2h"
        else:
            return "📧 STANDARD - Répondre sous 24h"

def get_confirmation_email(name, subject, project_type, message_content, locale='fr'):
    """Génère l'email de confirmation personnalisé (FR/EN)"""
    
    if locale == 'en':
        project_info = {
            'orientation': {
                'emoji': '🎓',
                'title': 'your orientation search',
                'next_steps': """
🎯 NEXT STEPS FOR YOUR ORIENTATION:

1. 📊 Get personalized support
   → https://www.wendogo.com/?tab=accompany#accompany-section

2. 📞 Book your discovery call (15 min free)
   → An expert analyzes your profile

3. 🎓 Receive your personalized recommendations
   → Among our 2100+ referenced programs

💡 TIP: Start with our simulator for an initial assessment!"""
            },
            
            'visa': {
                'emoji': '📋',
                'title': 'your student visa application',
                'next_steps': """
📋 NEXT STEPS FOR YOUR VISA:

1. 📖 Consult our complete guide
   → https://www.wendogo.com/guides/etudier-en-france

2. ✅ Check your Campus France eligibility
   → According to your country of residence

3. 🎯 Maximize your chances with our support
   → Complete application preparation

⚠️ IMPORTANT: Visa processing can be long, start early!"""
            },
            
            'campus-france': {
                'emoji': '🏛️',
                'title': 'the Campus France procedure',
                'next_steps': """
🏛️ CAMPUS FRANCE HELP:

1. 🌍 Check if your country is concerned
   → Complete list in our guide

2. 📋 Prepare your application step by step
   → Documents, deadlines, interview

3. 🎯 Benefit from our expertise
   → Specialized Campus France support

📅 DEADLINES: Start 6-8 months before your enrollment!"""
            },
            
            'default': {
                'emoji': '💼',
                'title': 'your study project in France',
                'next_steps': """
🚀 USEFUL RESOURCES FOR YOUR PROJECT:

• 📖 Complete guides: https://www.wendogo.com/guides/etudier-en-france
• 🔍 Search programs: https://www.wendogo.com
• 📊 Get support: https://www.wendogo.com/?tab=accompany#accompany-section
• 💬 Immediate support: WhatsApp +33 6 68 15 60 73"""
            }
        }
        
        info = project_info.get(project_type, project_info['default'])
        
        return f"""
Hello {name}! 👋

Thank you for your message {info['emoji']} {info['title']}.

✅ RECEIPT CONFIRMATION
We have received your request: "{subject}"

Our team of experts will analyze your situation and respond to you personally as soon as possible (usually within 2 hours during the day).

{info['next_steps']}

═══════════════════════════════════════════════════
🚀 NEED AN IMMEDIATE ANSWER?
═══════════════════════════════════════════════════

📧 Email: hello@wendogo.com
📱 WhatsApp: +33 6 68 15 60 73 (immediate response)
💬 Messenger: https://m.me/wendogoHQ
🌐 Website: https://www.wendogo.com

═══════════════════════════════════════════════════
📋 YOUR REQUEST SUMMARY
═══════════════════════════════════════════════════
Project type: {project_type} {info['emoji']}
Subject: {subject}
Date: {datetime.now().strftime('%m/%d/%Y at %H:%M')}

Your message:
{message_content}

═══════════════════════════════════════════════════

See you soon to make your study project in France a reality! 🇫🇷

The Wendogo Team 🎓

P.S.: Add hello@wendogo.com to your contacts so you don't miss any of our responses!
"""
    
    # Version française
    project_info = {
        'orientation': {
            'emoji': '🎓',
            'title': 'votre recherche d\'orientation',
            'next_steps': """
🎯 PROCHAINES ÉTAPES POUR VOTRE ORIENTATION :

1. 📊 Faites vous accomagner
   → https://www.wendogo.com/?tab=accompany#accompany-section

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
   → https://www.wendogo.com/guides/etudier-en-france

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

• 📖 Guides complets : https://www.wendogo.com/guides/etudier-en-france
• 🔍 Recherche formations : https://www.wendogo.com
• 📊 Faites vous accompanger : https://www.wendogo.com/?tab=accompany#accompany-section
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
🌐 Site web : https://www.wendogo.com

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

def get_admin_notification_email(name, email, subject, message_content, project_type, contact_message, request, locale='fr'):
    """Génère l'email de notification pour l'équipe admin (FR/EN)"""
    
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
    
    if locale == 'en':
        return f"""
{urgency_indicator} - NEW CONTACT MESSAGE

═══════════════════════════════════════════════════
📋 CONTACT INFORMATION
═══════════════════════════════════════════════════
👤 Name: {name}
📧 Email: {email}
{project_emoji} Type: {project_type.upper()}
📝 Subject: {subject}

═══════════════════════════════════════════════════
💬 CLIENT MESSAGE
═══════════════════════════════════════════════════
{message_content}

═══════════════════════════════════════════════════
🔧 TECHNICAL METADATA
═══════════════════════════════════════════════════
🕒 Received on: {datetime.now().strftime('%m/%d/%Y at %H:%M:%S')}
🌐 IP: {request.remote_addr}
💻 User-Agent: {request.headers.get('User-Agent', 'Not specified')[:100]}...
🆔 Message ID: {contact_message.id if contact_message else 'Not saved'}

═══════════════════════════════════════════════════
🚀 RECOMMENDED ACTIONS
═══════════════════════════════════════════════════
Type: {project_type} {project_emoji}

📋 SUGGESTED RESPONSE:
{get_response_template(project_type, locale)}

⏱️ RECOMMENDED RESPONSE TIME:
{get_response_urgency(project_type, locale)}

📊 ADMIN PANEL:
https://wendogo.com/admin (Messages tab)

---
Automatically sent from wendogo.com
Wendogo Notification System v2.0
"""
    
    # Version française
    return f"""
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
{get_response_template(project_type, locale)}

⏱️ DÉLAI DE RÉPONSE RECOMMANDÉ:
{get_response_urgency(project_type, locale)}

📊 ADMIN PANEL:
https://wendogo.com/admin (onglet Messages contact)

---
Envoyé automatiquement depuis wendogo.com
Système de notification Wendogo v2.0
"""

def init_routes(app):
    @app.route('/api/contact/send-message', methods=['POST'])
    def send_contact_message():
        try:
            current_app.logger.info("[DEBUG] ✅ Route /send-message triggered")
            locale = get_locale_from_request(request)
            # Récupérer les données du formulaire
            data = request.get_json()
            current_app.logger.info(f"[DEBUG] Payload: {data}")   

            if not data:
                current_app.logger.error("[DEBUG] ❌ No JSON data received")
                error_msg = 'No data received' if locale == 'en' else 'Aucune donnée reçue'
                return jsonify({'success': False, 'error': error_msg}), 400
                
            # Validation des données
            required_fields = ['name', 'email', 'subject', 'message', 'projectType']
            for field in required_fields:
                if not data.get(field) or not data[field].strip():
                    error_msg = f'The {field} field is required' if locale == 'en' else f'Le champ {field} est requis'
                    return jsonify({
                        'success': False,
                        'error': error_msg
                    }), 400
            current_app.logger.info(f"[DEBUG] MAIL_DEFAULT_SENDER: {current_app.config.get('MAIL_DEFAULT_SENDER')}")
            current_app.logger.info(f"[DEBUG] MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
            current_app.logger.info(f"[DEBUG] MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
                        
            # Validation email
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, data['email']):
                error_msg = 'Invalid email format' if locale == 'en' else 'Format email invalide'
                return jsonify({
                    'success': False,
                    'error': error_msg
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
            
            email_body = get_admin_notification_email(
                name, email, subject, message_content, project_type, 
                contact_message, request, locale
            )
            
            mail = current_app.extensions['mail']
            # Envoyer l'email à l'équipe
            msg = Message(
                subject=email_subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=['hello@wendogo.com'],
                reply_to=email,
                body=email_body
            )
            
            current_app.logger.info(f"[DEBUG] Sender: {current_app.config['MAIL_DEFAULT_SENDER']}")

            mail.send(msg)
            
            # Email de confirmation personnalisé
            if locale == 'en':
                confirmation_subject = "Your message has been received - Wendogo 🎓"
            else:
                confirmation_subject = "Votre message a bien été reçu - Wendogo 🎓"
                
            confirmation_body = get_confirmation_email(name, subject, project_type, message_content, locale)
            
            confirmation_msg = Message(
                subject=confirmation_subject,
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email],
                body=confirmation_body
            )
            
            mail.send(confirmation_msg)
            
            current_app.logger.info(f"Contact emails sent successfully for {email}")
            
            success_msg = 'Your message has been sent successfully! We will respond quickly.' if locale == 'en' else 'Votre message a été envoyé avec succès ! Nous vous répondrons rapidement.'
            
            return jsonify({
                'success': True,
                'message': success_msg,
                'message_id': contact_message.id if contact_message else None
            }), 200
            
        except Exception as e:
            print(f"❌ [CONTACT] Exception: {e}")
            print(f"❌ [CONTACT] Exception type: {type(e)}")
            import traceback
            print(f"❌ [CONTACT] Traceback: {traceback.format_exc()}")
            
            return jsonify({
                'success': False,
                'error': f'Exception: {str(e)}'
            }), 500

    @app.route('/api/contact/test', methods=['POST'])
    def test_contact():
        try:
            current_app.logger.info("✅ Test route hit")
            
            # Test configuration mail
            current_app.logger.info(f"MAIL config: {current_app.config.get('MAIL_DEFAULT_SENDER')}")
            mail = current_app.extensions['mail']
            # Test message simple
            msg = Message(
                subject="Test Wendogo",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=['hello@wendogo.com'],
                body="Test message from production"
            )
            
            mail.send(msg)
            current_app.logger.info("✅ Email sent successfully")
            
            return jsonify({'success': True, 'message': 'Test email sent'})
            
        except Exception as e:
            current_app.logger.error(f"❌ Test error: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
        
    @app.route("/debug/all-env")
    def all_env():
        import os
        from flask import jsonify

        return jsonify({k: v for k, v in os.environ.items() if 'MAIL' in k or 'NEXT' in k or 'FLASK' in k})

    @app.route('/debug/env', methods=['GET'])
    def debug_env():
        print("🔍 DEBUG ENVIRONMENT VARIABLES", flush=True)

        logger = logging.getLogger(__name__)

        # 🔍 Valeurs à inspecter
        working_dir = os.getcwd()
        env_exists = os.path.exists('.env')
        mail_server = os.getenv('MAIL_SERVER')
        mail_username = os.getenv('MAIL_USERNAME')
        mail_default_sender = os.getenv('MAIL_DEFAULT_SENDER')
        flask_config_sender = app.config.get('MAIL_DEFAULT_SENDER')

        # 📦 Log dans stdout (donc visible via tail -f /var/log/wendogo-app.out.log)
        logger.info("🔍 ENV CHECK — working_dir: %s", working_dir)
        logger.info("🔍 ENV CHECK — .env exists: %s", env_exists)
        logger.info("🔍 ENV CHECK — MAIL_SERVER: %s", mail_server)
        logger.info("🔍 ENV CHECK — MAIL_USERNAME: %s", mail_username)
        logger.info("🔍 ENV CHECK — MAIL_DEFAULT_SENDER: %s", mail_default_sender)
        logger.info("🔍 CONFIG CHECK — app.config['MAIL_DEFAULT_SENDER']: %s", flask_config_sender)

        return {
            'working_dir': working_dir,
            'env_exists': env_exists,
            'mail_server': mail_server,
            'mail_username': mail_username,
            'mail_default_sender': mail_default_sender,
            'flask_config_sender': flask_config_sender
        }
    
    @app.route('/api/contact/ping', methods=['POST'])
    def ping_contact():
        try:
            data = request.get_json()
            current_app.logger.info(f"✅ Ping reçu: {data}")
            return jsonify({'success': True, 'received': data})
        except Exception as e:
            current_app.logger.error(f"❌ Ping error: {e}")
            return jsonify({'success': False, 'error': str(e)})
        
    @app.route('/api/contact/test-email', methods=['POST'])
    def test_email_config():
        """Route de test pour vérifier la configuration email"""
        try:
            mail = current_app.extensions['mail']
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
