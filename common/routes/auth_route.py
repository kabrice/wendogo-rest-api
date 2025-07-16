
# ═══════════════════════════════════════════════════════════
# 📁 common/routes/auth_route.py (NOUVEAU)
# ═══════════════════════════════════════════════════════════

from flask import request, jsonify, session, current_app
from flask_mail import Mail, Message
import datetime
import bcrypt

mail = Mail()
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from common.models.user import User
from common.models.user_favorite import UserFavorite
from common.models import db
from common.models.lead_level_value_relation import LeadLevelValueRelation
from common.models.lead_subject_relation import LeadSubjectRelation
from common.models.visa_criteria_lead_relation import VisaCriteriaLeadRelation
from common.models.lead import Lead  # Ajout de l'import manquant pour Lead
from common.models.report_card import ReportCard  # Ajout de l'import manquant
from common.models.report_card_subject_relation import ReportCardSubjectRelation  # Ajout de l'import manquant
from common.models.award import Award  # Ajout de l'import manquant pour Award
from common.models.work_experience import WorkExperience  # Ajout de l'import manquant pour WorkExperience
from common.models.traveling import Traveling  # Ajout de l'import manquant pour Traveling
from common.models.json_input import JsonInput  # Ajout de l'import manquant pour Json
from common.models.passport import Passport  # Ajout de l'import manquant pour Passport
from common.models.email_verification_token import EmailVerificationToken  # Import du modèle EmailVerificationToken
from common.models.password_reset_token import PasswordResetToken  # Import du modèle PasswordResetToken
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt
import datetime
import os

def get_email_base_template():
    """Template de base pour tous les emails Wendogo"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title} - Wendogo</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <!-- Header unifié -->
        <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">{header_title} ! {icon}</h1>
        </div>        
        <!-- Contenu principal -->
        <div style="background: #ffffff; padding: 40px 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {content}
        </div>
        
        <!-- Footer unifié -->
        <div style="text-align: center; margin-top: 30px; padding: 20px; color: #6b7280; font-size: 14px;">
            <div style="border-top: 1px solid #e5e7eb; padding-top: 20px;">
                <p style="margin: 0 0 10px 0;">
                    <strong>Wendogo</strong> - Votre partenaire pour étudier en France
                </p>
                <p style="margin: 0 0 15px 0;">
                    🎓 Plus de 2100+ formations privées | 🏫 500+ écoles | 🌟 Accompagnement personnalisé
                </p>
                <div style="margin: 15px 0;">
                    <a href="https://wendogo.com" style="color: #667eea; text-decoration: none; margin: 0 10px;">Site web</a>
                    <a href="https://wendogo.com/contact" style="color: #667eea; text-decoration: none; margin: 0 10px;">Contact</a>
                </div>
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #9ca3af;">
                    © 2025 Wendogo. Tous droits réservés.<br>
                    Vous recevez cet email car vous avez créé un compte sur Wendogo.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_verification_email_template(email_data):
    """Template unifié pour l'email de vérification"""
    base_template = get_email_base_template()
    
    content = f"""
        <p style="font-size: 16px; color: #374151; line-height: 1.6; margin-bottom: 20px;">
            Bonjour <strong>{email_data.get('firstname', 'Utilisateur')}</strong>,
        </p>
        
        <p style="font-size: 16px; color: #374151; line-height: 1.6; margin-bottom: 25px;">
            Merci de vous être inscrit sur Wendogo ! Pour activer votre compte et commencer à explorer 
            plus de <strong>2100+ formations privées</strong> dans <strong>500+ écoles françaises</strong>, 
            veuillez vérifier votre adresse email en cliquant sur le bouton ci-dessous.
        </p>
        
        <div style="text-align: center; margin: 35px 0;">
            <a href="{email_data.get('verificationUrl')}" 
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; 
                      padding: 16px 32px; 
                      text-decoration: none; 
                      border-radius: 25px; 
                      font-size: 16px; 
                      font-weight: bold;
                      display: inline-block;
                      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                      transition: all 0.3s ease;">
                ✅ Vérifier mon email
            </a>
        </div>
        
        <div style="background: #f3f4f6; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 4px solid #667eea;">
            <p style="margin: 0; font-size: 14px; color: #6b7280;">
                <strong>⏰ Important :</strong> Ce lien expire dans <strong>{email_data.get('expiresIn', '24 heures')}</strong>
            </p>
        </div>
        
        <div style="margin-top: 30px; padding-top: 25px; border-top: 1px solid #e5e7eb;">
            <p style="font-size: 14px; color: #6b7280; margin-bottom: 15px;">
                <strong>Vous n'arrivez pas à cliquer sur le bouton ?</strong><br>
                Copiez et collez ce lien dans votre navigateur :
            </p>
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; word-break: break-all;">
                <a href="{email_data.get('verificationUrl')}" style="color: #667eea; font-size: 14px; text-decoration: none;">
                    {email_data.get('verificationUrl')}
                </a>
            </div>
        </div>
        
        <p style="font-size: 14px; color: #9ca3af; margin-top: 25px; text-align: center;">
            Si vous n'avez pas créé de compte sur Wendogo, vous pouvez ignorer cet email en toute sécurité.
        </p>
    """
    
    return base_template.format(
        title="Vérifiez votre compte",
        icon="🎓",
        header_title="Bienvenue sur Wendogo !",
        header_subtitle="Vérifiez votre email pour commencer votre aventure académique",
        content=content
    )

def get_password_reset_email_template(email_data):
    """Template unifié pour l'email de réinitialisation (même design que vérification)"""
    base_template = get_email_base_template()
    
    content = f"""
        <p style="font-size: 16px; color: #374151; line-height: 1.6; margin-bottom: 20px;">
            Bonjour,
        </p>
        
        <p style="font-size: 16px; color: #374151; line-height: 1.6; margin-bottom: 25px;">
            Vous avez demandé la réinitialisation de votre mot de passe sur Wendogo. 
            Pas d'inquiétude, cela arrive ! Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe sécurisé.
        </p>
        
        <div style="text-align: center; margin: 35px 0;">
            <a href="{email_data.get('resetUrl')}" 
               style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; 
                      padding: 16px 32px; 
                      text-decoration: none; 
                      border-radius: 25px; 
                      font-size: 16px; 
                      font-weight: bold;
                      display: inline-block;
                      box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                      transition: all 0.3s ease;">
                🔄 Réinitialiser mon mot de passe
            </a>
        </div>
        
        <div style="background: #fef3cd; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 4px solid #f59e0b;">
            <p style="margin: 0; font-size: 14px; color: #92400e;">
                <strong>⏰ Attention :</strong> Ce lien expire dans <strong>{email_data.get('expiresIn', '1 heure')}</strong> pour votre sécurité.
            </p>
        </div>
        
        <div style="background: #ecfdf5; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 4px solid #10b981;">
            <p style="margin: 0; font-size: 14px; color: #065f46;">
                <strong>🛡️ Sécurité :</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. 
                Votre mot de passe actuel reste inchangé.
            </p>
        </div>
        
        <div style="margin-top: 30px; padding-top: 25px; border-top: 1px solid #e5e7eb;">
            <p style="font-size: 14px; color: #6b7280; margin-bottom: 15px;">
                <strong>Vous n'arrivez pas à cliquer sur le bouton ?</strong><br>
                Copiez et collez ce lien dans votre navigateur :
            </p>
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb; word-break: break-all;">
                <a href="{email_data.get('resetUrl')}" style="color: #667eea; font-size: 14px; text-decoration: none;">
                    {email_data.get('resetUrl')}
                </a>
            </div>
        </div>
        
        <p style="font-size: 14px; color: #9ca3af; margin-top: 25px; text-align: center;">
            Cet email a été envoyé automatiquement, veuillez ne pas y répondre.
        </p>
    """
    
    return base_template.format(
        title="Réinitialisation de votre mot de passe",
        icon="🔐",
        header_title="Réinitialisation de mot de passe",
        header_subtitle="Définissez un nouveau mot de passe pour votre compte",
        content=content
    )


def init_routes(app):
    
    @app.route('/auth/oauth-signin', methods=['POST'])
    def oauth_signin():
        """Authentification OAuth (Google/Facebook)"""
        data = request.json
        
        try:
            provider = data.get('provider')
            provider_id = data.get('provider_id')
            email = data.get('email')
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            avatar_url = data.get('avatar_url')
            
            # Chercher utilisateur existant
            user = None
            if provider == 'google':
                user = User.query.filter_by(google_id=provider_id).first()
            elif provider == 'facebook':
                user = User.query.filter_by(facebook_id=provider_id).first()
            
            # Si pas trouvé par provider_id, chercher par email
            if not user and email:
                user = User.query.filter_by(email=email).first()
                
            if user:
                # Mettre à jour les infos OAuth
                if provider == 'google':
                    user.google_id = provider_id
                elif provider == 'facebook':
                    user.facebook_id = provider_id
                    
                user.avatar_url = avatar_url
                user.provider = provider
                user.email_verified = True
                user.last_login = datetime.datetime.utcnow()
                
            else:
                # Créer nouvel utilisateur
                user = User(
                    firstname=firstname,
                    lastname=lastname,
                    email=email,
                    provider=provider,
                    avatar_url=avatar_url,
                    email_verified=True,
                    last_login=datetime.datetime.utcnow()
                )
                
                if provider == 'google':
                    user.google_id = provider_id
                elif provider == 'facebook':
                    user.facebook_id = provider_id
                    
                db.session.add(user)
            
            db.session.commit()
            
            # Générer JWT token
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'avatar_url': user.avatar_url
                },
                'token': token
            })
            
        except Exception as e:
            print(f"Erreur OAuth signin: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/login', methods=['POST'])
    def login():
        """Authentification classique email/password avec vérifications"""
        data = request.json   
            
        try:
            email = data.get('email')
            password = data.get('password')
            
            print(f"🔍 Tentative de connexion: {email}")
            
            if not email or not password:
                return jsonify({'success': False, 'error': 'Email et mot de passe requis'}), 400
            
            # Chercher l'utilisateur
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ Utilisateur non trouvé: {email}")
                return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401
            
            # Vérifier le mot de passe
            if not user.password:
                print(f"❌ Pas de mot de passe défini pour: {email}")
                return jsonify({'success': False, 'error': 'Compte créé via OAuth - utilisez Google/Facebook'}), 401
            
            # Utiliser check_password_hash si le mot de passe est hashé avec werkzeug
            # Sinon, comparaison directe (si déjà hashé avec bcrypt côté Next.js)
            password_valid = False
            try:
                #from werkzeug.security import check_password_hash
                password_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
            except:
                # Fallback: comparaison directe si le mot de passe est déjà hashé avec bcrypt
                password_valid = (user.password == password)
            
            if not password_valid:
                print(f"❌ Mot de passe incorrect pour: {email}")
                return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401
            
            # ✅ NOUVEAU: Vérifier si l'email est vérifié
            if not user.email_verified:
                print(f"⚠️ Email non vérifié pour: {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Email non vérifié',
                    'error_code': 'EMAIL_NOT_VERIFIED',
                    'user_id': user.id
                }), 403
            
            # Mettre à jour la dernière connexion
            user.last_login = db.session.execute(db.select(db.func.current_timestamp())).scalar()
            db.session.commit()
            
            print(f"✅ Connexion réussie pour: {email}")
            
            # Générer JWT token (optionnel)
            token = None
            try:
                token = jwt.encode({
                    'user_id': user.id,
                    'email': user.email,
                    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
                }, app.config.get('SECRET_KEY', 'fallback-secret'), algorithm='HS256')
            except Exception as e:
                print(f"⚠️ Erreur génération JWT: {e}")
            print(f"🔑 Token généré pour: {email[:10]}... -> {token[:10] if token else 'None'}")
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'avatar_url': user.avatar_url,
                    'email_verified': user.email_verified,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'token': token
            })
            
        except Exception as e:
            print(f"❌ Erreur login: {e}")
            return jsonify({'success': False, 'error': 'Erreur serveur'}), 500
  

    @app.route('/auth/check-email', methods=['POST'])
    def check_email():
        """Vérifier si un email existe déjà"""
        data = request.json
        
        try:
            email = data.get('email')
            if not email:
                return jsonify({'success': False, 'error': 'Email requis'}), 400
            
            # Vérifier si l'email existe
            existing_user = User.query.filter_by(email=email).first()
            
            return jsonify({
                'success': True,
                'exists': existing_user is not None
            })
            
        except Exception as e:
            print(f"Erreur check email: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/register', methods=['POST'])
    def register_extended():
        """Inscription avec champs étendus"""
        data = request.json
        
        try:
            email = data.get('email')
            password = data.get('password')
            firstname = data.get('firstname')
            lastname = data.get('lastname')
            phone = data.get('phone')
            birthdate_str = data.get('birthdate')
            country = data.get('country')
            
            print(f"🔍 Données reçues: {data}")  # Debug
            
            # Validation des champs requis
            required_fields = ['email', 'password', 'firstname', 'lastname', 'phone', 'birthdate', 'country']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'{field} requis'}), 400
            
            # Vérifier si email existe déjà
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'success': False, 'error': 'Email déjà utilisé'}), 400
            
            # Convertir la date de naissance - ✅ CORRIGÉ
            try:
                birthdate = datetime.datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Format de date invalide'}), 400
            
            # ✅ CRÉER l'utilisateur avec le bon constructeur
            user = User(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=password,  # Déjà hashé côté Next.js
                phone=phone,
                birthdate=birthdate,
                country=country,
                provider='email',
                email_verified=False
            )
            
            print(f"🔍 Utilisateur créé: {user.email}")  # Debug
            
            db.session.add(user)
            db.session.commit()
            
            print(f"✅ Utilisateur sauvegardé avec ID: {user.id}")  # Debug
            
            return jsonify({
                'success': True,
                'message': 'Compte créé avec succès',
                'id': user.id,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'phone': user.phone,
                'birthdate': user.birthdate.isoformat() if user.birthdate else None,
                'country': user.country
            })
            
        except Exception as e:
            print(f"❌ Erreur register: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        # Ajout à votre auth_route.py

    @app.route('/auth/delete-user-data', methods=['POST'])
    def delete_user_data():
        """Supprimer toutes les données d'un utilisateur (RGPD/Facebook)"""
        
        # Vérifier la clé API interne
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('INTERNAL_API_KEY', 'your-internal-secret-key'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.json
        
        try:
            facebook_id = data.get('facebook_id')
            deletion_type = data.get('deletion_type', 'user_request')
            
            if not facebook_id:
                return jsonify({'success': False, 'error': 'facebook_id requis'}), 400
            
            # Trouver l'utilisateur par Facebook ID
            user = User.query.filter_by(facebook_id=facebook_id).first()
            
            if not user:
                # L'utilisateur n'existe pas dans notre base
                return jsonify({
                    'success': True, 
                    'message': 'Utilisateur non trouvé - aucune donnée à supprimer',
                    'user_found': False
                })
            
            user_id = user.id
            user_email = user.email
            
            # Commencer une transaction pour supprimer toutes les données
            with db_transaction():
                # 1. Supprimer les favoris
                UserFavorite.query.filter_by(user_id=user_id).delete()
                
                # 2. Supprimer les données de lead/simulation si elles existent
                if hasattr(user, 'leads'):
                    for lead in user.leads:
                        # Supprimer les relations liées au lead
                        LeadLevelValueRelation.query.filter_by(lead_id=lead.id).delete()
                        LeadSubjectRelation.query.filter_by(lead_id=lead.id).delete()
                        VisaCriteriaLeadRelation.query.filter_by(lead_id=lead.id).delete()
                        
                        # Supprimer les report cards et leurs relations
                        report_cards = ReportCard.query.filter_by(lead_id=lead.id).all()
                        for rc in report_cards:
                            ReportCardSubjectRelation.query.filter_by(report_card_id=rc.id).delete()
                        ReportCard.query.filter_by(lead_id=lead.id).delete()
                        
                        # Supprimer autres données liées
                        Award.query.filter_by(lead_id=lead.id).delete()
                        WorkExperience.query.filter_by(lead_id=lead.id).delete()
                        Traveling.query.filter_by(lead_id=lead.id).delete()
                        JsonInput.query.filter_by(lead_id=lead.id).delete()
                    
                    # Supprimer les leads
                    Lead.query.filter_by(user_id=user_id).delete()
                
                # 3. Supprimer le passeport si il existe
                if user.passport_id:
                    Passport.query.filter_by(id=user.passport_id).delete()
                
                # 4. Anonymiser ou supprimer l'utilisateur
                if deletion_type == 'facebook_request':
                    # Pour Facebook, on peut anonymiser au lieu de supprimer complètement
                    user.firstname = f"[Supprimé-{user_id}]"
                    user.lastname = "[Supprimé]"
                    user.email = f"deleted_{user_id}@deleted.local"
                    user.facebook_id = None
                    user.google_id = None
                    user.avatar_url = None
                    user.phone = None
                    user.address = None
                    user.description = None
                    user.password = None
                    user.updated_at = datetime.utcnow()
                else:
                    # Suppression complète pour les demandes utilisateur directes
                    db.session.delete(user)
            
            # Log de la suppression
            print(f"Données utilisateur supprimées - ID: {user_id}, Email: {user_email}, Type: {deletion_type}")
            
            return jsonify({
                'success': True,
                'message': 'Données utilisateur supprimées avec succès',
                'user_found': True,
                'user_id': user_id,
                'deletion_type': deletion_type
            })
            
        except Exception as e:
            print(f"Erreur suppression données utilisateur: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/save-verification-token', methods=['POST'])
    def save_verification_token():
        """Sauvegarder un token de vérification"""
        data = request.json
        
        try:
            email = data.get('email')
            token = data.get('token')
            expires_at_str = data.get('expires_at')
            
            if not all([email, token, expires_at_str]):
                return jsonify({'success': False, 'error': 'Données manquantes'}), 400
            
            expires_at = datetime.datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            
            # Supprimer les anciens tokens pour cet email
            EmailVerificationToken.query.filter_by(email=email).delete()
            
            # Créer le nouveau token
            verification_token = EmailVerificationToken(
                email=email,
                token=token,
                expires_at=expires_at
            )
            
            db.session.add(verification_token)
            db.session.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"Erreur sauvegarde token: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/send-verification-email', methods=['POST'])
    def send_verification_email():
        """Envoyer un email de vérification"""
        data = request.json
        
        try:
            to_email = data.get('to')
            subject = data.get('subject', 'Vérifiez votre compte Wendogo')
            email_data = data.get('data', {})
            
            if not to_email:
                return jsonify({'success': False, 'error': 'Email destinataire requis'}), 400
            
            # Template HTML de l'email
            html_body = get_verification_email_template(email_data)
            html_bodys = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Vérification email - Wendogo</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">Bienvenue sur Wendogo ! 🎓</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px; color: #333;">Bonjour <strong>{email_data.get('firstname', 'Utilisateur')}</strong>,</p>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        Merci de vous être inscrit sur Wendogo ! Pour activer votre compte et commencer à explorer 
                        plus de <strong>2100+ formations privées</strong> dans <strong>500+ écoles françaises</strong>, 
                        veuillez vérifier votre adresse email.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{email_data.get('verificationUrl')}" 
                        style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; 
                                padding: 15px 30px; 
                                text-decoration: none; 
                                border-radius: 25px; 
                                font-size: 16px; 
                                font-weight: bold;
                                display: inline-block;">
                            ✅ Vérifier mon email
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; text-align: center;">
                        Ce lien expire dans <strong>{email_data.get('expiresIn', '24 heures')}</strong>
                    </p>
                    
                    <hr style="border: none; height: 1px; background: #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 14px; color: #666;">
                        Si vous n'arrivez pas à cliquer sur le bouton, copiez ce lien dans votre navigateur :<br>
                        <a href="{email_data.get('verificationUrl')}" style="color: #667eea; word-break: break-all;">
                            {email_data.get('verificationUrl')}
                        </a>
                    </p>
                    
                    <p style="font-size: 14px; color: #666;">
                        Si vous n'avez pas créé de compte sur Wendogo, ignorez cet email.
                    </p>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                        <p style="font-size: 14px; color: #999; margin: 0;">
                            © 2025 Wendogo - Votre avenir académique en France
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Envoyer l'email
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            
            mail.send(msg)
            
            return jsonify({'success': True, 'message': 'Email envoyé'})
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/auth/verify-token', methods=['POST'])
    def verify_token():
        """Vérifier un token de vérification email"""
        data = request.json
        
        try:
            token = data.get('token')
            email = data.get('email')
            
            print(f"🔍 Route verify-token appelée - Email: {email}, Token: {token[:10] if token else 'None'}...")
            
            if not token or not email:
                return jsonify({'success': False, 'error': 'Token et email requis'}), 400
            
            # Chercher le token
            verification_token = EmailVerificationToken.query.filter_by(
                token=token,
                email=email,
                used=False
            ).first()
            
            if not verification_token:
                print(f"❌ Token non trouvé ou déjà utilisé")
                return jsonify({'success': False, 'error': 'Token invalide ou déjà utilisé'}), 400
            
            # Vérifier l'expiration - ✅ CORRIGÉ
            current_time = db.session.execute(db.select(db.func.current_timestamp())).scalar()
            print(f"🕐 Vérification expiration - Current: {current_time}, Expires: {verification_token.expires_at}")
            
            if verification_token.expires_at < current_time:
                print(f"❌ Token expiré")
                return jsonify({'success': False, 'error': 'Token expiré'}), 400
            
            # Marquer le token comme utilisé
            verification_token.used = True
            print(f"✅ Token marqué comme utilisé")
            
            # Marquer l'utilisateur comme vérifié
            user = User.query.filter_by(email=email).first()
            if user:
                user.email_verified = True
                print(f"✅ Utilisateur {email} marqué comme vérifié")
                # updated_at sera mis à jour automatiquement par le listener
            else:
                print(f"⚠️ Utilisateur {email} non trouvé")
            
            db.session.commit()
            print(f"✅ Changements sauvegardés en base")
            
            return jsonify({'success': True, 'message': 'Email vérifié avec succès'})
            
        except Exception as e:
            print(f"❌ Erreur vérification token: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
       
    @app.route('/test-email', methods=['POST'])
    def test_email():
        """Route pour tester l'envoi d'email"""
        try:
            print("Envoi d'email de test...🥰 "+ app.config['MAIL_DEFAULT_SENDER'])
            msg = Message(
                subject='Test Email Wendogo',
                recipients=['edgarkamdem1@gmail.com'],
                html="""
                <h2>Test Email</h2>
                <p>Si vous recevez cet email, la configuration fonctionne !</p>
                """,
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            
            mail.send(msg)
            return jsonify({'success': True, 'message': 'Email de test envoyé'})
            
        except Exception as e:
            print(f"Erreur test email: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500        
        
    # Mise à jour de la route login dans auth_route.py

    @app.route('/auth/save-reset-token', methods=['POST'])
    def save_reset_token():
        """Sauvegarder un token de réinitialisation"""
        data = request.json
        
        try:
            email = data.get('email')
            token = data.get('token')
            expires_at_str = data.get('expires_at')
            
            if not all([email, token, expires_at_str]):
                return jsonify({'success': False, 'error': 'Données manquantes'}), 400
            
            # Convertir la date d'expiration
            try:
                expires_at = datetime.datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'success': False, 'error': 'Format de date invalide'}), 400
            
            # Supprimer les anciens tokens pour cet email
            PasswordResetToken.query.filter_by(email=email).delete()
            
            # Créer le nouveau token
            reset_token = PasswordResetToken(
                email=email,
                token=token,
                expires_at=expires_at
            )
            
            db.session.add(reset_token)
            db.session.commit()
            
            print(f"✅ Token de reset sauvegardé pour: {email}")
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde token reset: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/send-reset-email', methods=['POST'])
    def send_reset_email():
        """Envoyer un email de réinitialisation"""
        data = request.json
        
        try:
            to_email = data.get('to')
            subject = data.get('subject', 'Réinitialisation de votre mot de passe')
            email_data = data.get('data', {})
            
            if not to_email:
                return jsonify({'success': False, 'error': 'Email destinataire requis'}), 400
            
            # Template HTML de l'email de reset
            html_body = get_password_reset_email_template(email_data)
            # Envoyer l'email
            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_body
            )
            
            mail.send(msg)
            
            print(f"✅ Email de reset envoyé à: {to_email}")
            return jsonify({'success': True, 'message': 'Email de réinitialisation envoyé'})
            
        except Exception as e:
            print(f"❌ Erreur envoi email reset: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/verify-reset-token', methods=['POST'])
    def verify_reset_token():
        """Vérifier un token de réinitialisation"""
        data = request.json
        
        try:
            token = data.get('token')
            email = data.get('email')
            
            if not token or not email:
                return jsonify({'success': False, 'error': 'Token et email requis'}), 400
            
            # Chercher le token
            reset_token = PasswordResetToken.query.filter_by(
                token=token,
                email=email,
                used=False
            ).first()
            
            if not reset_token:
                return jsonify({'success': False, 'error': 'Token invalide ou déjà utilisé'}), 400
            
            # Vérifier l'expiration
            current_time = db.session.execute(db.select(db.func.current_timestamp())).scalar()
            if reset_token.expires_at < current_time:
                return jsonify({'success': False, 'error': 'Token expiré'}), 400
            
            return jsonify({'success': True, 'message': 'Token valide'})
            
        except Exception as e:
            print(f"❌ Erreur vérification token reset: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/auth/reset-password', methods=['POST'])
    def reset_password():
        """Réinitialiser le mot de passe"""
        data = request.json
        
        try:
            token = data.get('token')
            email = data.get('email')
            new_password = data.get('new_password')
            
            if not all([token, email, new_password]):
                return jsonify({'success': False, 'error': 'Tous les champs requis'}), 400
            
            if len(new_password) < 6:
                return jsonify({'success': False, 'error': 'Mot de passe trop court'}), 400
            
            # Vérifier le token
            reset_token = PasswordResetToken.query.filter_by(
                token=token,
                email=email,
                used=False
            ).first()
            
            if not reset_token:
                return jsonify({'success': False, 'error': 'Token invalide'}), 400
            
            # Vérifier l'expiration
            current_time = db.session.execute(db.select(db.func.current_timestamp())).scalar()
            if reset_token.expires_at < current_time:
                return jsonify({'success': False, 'error': 'Token expiré'}), 400
            
            # Trouver l'utilisateur
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({'success': False, 'error': 'Utilisateur non trouvé'}), 400
            
            # Mettre à jour le mot de passe (déjà hashé côté client)
            user.password = new_password
            
            # Marquer le token comme utilisé
            reset_token.used = True
            
            db.session.commit()
            
            print(f"✅ Mot de passe réinitialisé pour: {email}")
            return jsonify({'success': True, 'message': 'Mot de passe réinitialisé avec succès'})
            
        except Exception as e:
            print(f"❌ Erreur reset password: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500    
    
    @contextmanager
    def db_transaction():
        """Context manager pour les transactions de base de données"""
        try:
            yield
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

