# common/admin_manager.py - Gestionnaire modulaire pour l'admin

"""
Gestionnaire modulaire pour l'administration Wendogo
Peut être appelé depuis app.py ou utilisé comme script standalone
"""

import os
import secrets
import bcrypt
from datetime import datetime
from flask import current_app
from flask_mail import Message

class AdminManager:
    """Gestionnaire pour toutes les opérations admin"""
    
    def __init__(self, app=None, db=None, mail=None):
        self.app = app
        self.db = db
        self.mail = mail
        
    def init_app(self, app, db, mail):
        """Initialiser avec l'app Flask"""
        self.app = app
        self.db = db
        self.mail = mail
        
    def create_admin_user(self, send_email=True):
        """Créer l'utilisateur admin avec toutes les vérifications"""
        try:
            print("🔧 Création/vérification de l'utilisateur admin...")
            
            from common.models.user import User
            
            # Vérifier si l'admin existe déjà
            admin_user = User.query.filter_by(email='admin@wendogo.com').first()
            
            if admin_user:
                print(f"ℹ️ Utilisateur admin existe déjà (ID: {admin_user.id})")
                
                # Vérifier et corriger l'ID si nécessaire
                if admin_user.id != 1:
                    return self._fix_admin_id(admin_user)
                
                return True, None, "Admin existe déjà"
            
            else:
                return self._create_new_admin(send_email)
                
        except Exception as e:
            print(f"❌ Erreur création admin : {e}")
            if self.db:
                self.db.session.rollback()
            return False, None, str(e)
    
    def _create_new_admin(self, send_email=True):
        """Créer un nouvel utilisateur admin"""
        try:
            from common.models.user import User
            
            print("🆕 Création du compte admin...")
            
            # Générer un mot de passe sécurisé
            initial_password = secrets.token_urlsafe(16)
            password_hash = bcrypt.hashpw(initial_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Gérer les conflits d'ID
            self._handle_id_conflicts()
            
            # Créer l'utilisateur admin
            admin_user = User(
                firstname='Admin',
                lastname='Wendogo',
                email='admin@wendogo.com',
                password=password_hash,
                provider='admin',
                email_verified=True,
                created_at=datetime.utcnow()
            )
            
            # Ajouter et forcer l'ID à 1
            self.db.session.add(admin_user)
            self.db.session.flush()
            
            # Force l'ID à 1 via SQL brut
            self.db.session.execute(self.db.text("UPDATE user SET id = 1 WHERE email = 'admin@wendogo.com'"))
            self.db.session.commit()
            
            # Recharger l'objet
            admin_user = User.query.filter_by(email='admin@wendogo.com').first()
            
            print(f"✅ Compte admin créé avec ID: {admin_user.id}")
            print(f"🔑 Mot de passe initial: {initial_password}")
            
            # Envoyer le mot de passe à Brice
            if send_email and self.mail:
                self._send_admin_credentials(initial_password)
            
            return True, initial_password, "Admin créé avec succès"
            
        except Exception as e:
            print(f"❌ Erreur création nouvel admin : {e}")
            self.db.session.rollback()
            raise
    
    def _fix_admin_id(self, admin_user):
        """Corriger l'ID de l'admin s'il n'est pas 1"""
        try:
            print(f"🔧 Correction de l'ID admin : {admin_user.id} → 1")
            
            old_id = admin_user.id
            
            # Mettre à jour l'ID
            self.db.session.execute(
                self.db.text("UPDATE user SET id = 1 WHERE email = 'admin@wendogo.com'")
            )
            self.db.session.commit()
            
            print(f"✅ ID admin corrigé vers 1")
            
            # Mettre à jour les clés étrangères
            self._update_foreign_keys(old_id, 1)
            
            return True, None, "ID admin corrigé"
            
        except Exception as e:
            print(f"❌ Erreur correction ID : {e}")
            self.db.session.rollback()
            raise
    
    def _handle_id_conflicts(self):
        """Gérer les conflits d'ID lors de la création"""
        try:
            from common.models.user import User
            
            # Vérifier qu'aucun utilisateur n'a l'ID 1
            existing_user_id_1 = User.query.filter_by(id=1).first()
            if existing_user_id_1:
                print(f"⚠️ Utilisateur avec ID 1 existe déjà : {existing_user_id_1.email}")
                
                # Trouver le prochain ID disponible
                max_id_result = self.db.session.execute(self.db.text("SELECT MAX(id) FROM user")).fetchone()
                max_id = max_id_result[0] if max_id_result[0] else 0
                new_id = max_id + 1
                
                # Mettre à jour l'utilisateur existant
                self.db.session.execute(
                    self.db.text(f"UPDATE user SET id = {new_id} WHERE id = 1")
                )
                self.db.session.commit()
                print(f"✅ Ancien utilisateur ID 1 déplacé vers ID {new_id}")
                
        except Exception as e:
            print(f"❌ Erreur gestion conflits ID : {e}")
            raise
    
    def _update_foreign_keys(self, old_id, new_id):
        """Mettre à jour les clés étrangères"""
        try:
            # Tables qui pourraient référencer l'utilisateur admin
            tables_to_update = [
                'accompany_requests',
                'admin_sessions', 
                'admin_password_resets',
                'leads'
            ]
            
            for table in tables_to_update:
                try:
                    # Vérifier si la table existe
                    result = self.db.session.execute(
                        self.db.text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    ).fetchone()
                    
                    if result:
                        # Mettre à jour les références
                        self.db.session.execute(
                            self.db.text(f"UPDATE {table} SET user_id = {new_id} WHERE user_id = {old_id}")
                        )
                        print(f"  ✅ Mis à jour les références dans {table}")
                except Exception as e:
                    print(f"  ⚠️ Erreur mise à jour {table}: {e}")
            
            self.db.session.commit()
            
        except Exception as e:
            print(f"❌ Erreur mise à jour clés étrangères: {e}")
    
    def reset_admin_password(self, send_email=True):
        """Réinitialiser le mot de passe admin"""
        try:
            from common.models.user import User
            
            print("🔄 Réinitialisation du mot de passe admin...")
            
            # Trouver l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            
            if not admin_user:
                return False, None, "Utilisateur admin non trouvé"
            
            # Générer un nouveau mot de passe
            new_password = secrets.token_urlsafe(16)
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Mettre à jour
            admin_user.password = password_hash
            self.db.session.commit()
            
            print(f"✅ Nouveau mot de passe généré: {new_password}")
            
            # Envoyer à Brice
            if send_email and self.mail:
                self._send_admin_credentials(new_password, is_reset=True)
            
            return True, new_password, "Mot de passe réinitialisé"
            
        except Exception as e:
            print(f"❌ Erreur reset mot de passe: {e}")
            self.db.session.rollback()
            return False, None, str(e)
    
    def verify_admin_setup(self):
        """Vérifier la configuration admin"""
        try:
            from common.models.user import User
            
            print("🔍 Vérification de la configuration admin...")
            
            # Vérifier l'admin
            admin_user = User.query.filter_by(id=1, email='admin@wendogo.com').first()
            
            if not admin_user:
                return False, "Utilisateur admin non trouvé"
                
            issues = []
            
            if admin_user.id != 1:
                issues.append(f"ID admin incorrect : {admin_user.id} (attendu: 1)")
                
            if admin_user.email != 'admin@wendogo.com':
                issues.append(f"Email admin incorrect : {admin_user.email}")
                
            if not admin_user.password:
                issues.append("Mot de passe admin manquant")
                
            if not admin_user.email_verified:
                print("⚠️ Email admin non vérifié - Correction automatique...")
                admin_user.email_verified = True
                self.db.session.commit()
                print("✅ Email admin marqué comme vérifié")
            
            if issues:
                return False, "; ".join(issues)
            
            print("✅ Configuration admin vérifiée avec succès")
            print(f"   - ID: {admin_user.id}")
            print(f"   - Email: {admin_user.email}")
            print(f"   - Mot de passe: {'✅ Configuré' if admin_user.password else '❌ Manquant'}")
            print(f"   - Email vérifié: {'✅' if admin_user.email_verified else '❌'}")
            
            return True, "Configuration admin OK"
            
        except Exception as e:
            return False, f"Erreur vérification : {str(e)}"
    
    def create_security_tables(self):
        """Créer les tables de sécurité si elles n'existent pas"""
        try:
            print("🔧 Création des tables de sécurité...")
            
            security_tables_sql = """
            -- Table des sessions admin
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_id VARCHAR(255) UNIQUE NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                logged_out_at DATETIME,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES user (id)
            );

            -- Table des logs de sécurité
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type VARCHAR(100) NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent TEXT,
                additional_data JSON,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                severity VARCHAR(20) DEFAULT 'INFO'
            );

            -- Table des réinitialisations de mot de passe admin
            CREATE TABLE IF NOT EXISTS admin_password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reset_token VARCHAR(255) UNIQUE NOT NULL,
                requested_by_email VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                used_at DATETIME,
                is_used BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES user (id)
            );
            """
            
            # Exécuter le SQL
            for statement in security_tables_sql.split(';'):
                statement = statement.strip()
                if statement:
                    self.db.session.execute(self.db.text(statement))
            
            self.db.session.commit()
            print("✅ Tables de sécurité créées avec succès")
            return True
            
        except Exception as e:
            print(f"❌ Erreur création tables : {e}")
            self.db.session.rollback()
            return False
    
    def _send_admin_credentials(self, password, is_reset=False):
        """Envoyer les identifiants admin à Brice"""
        try:
            if not self.mail:
                print("⚠️ Mail non configuré - impossible d'envoyer l'email")
                return False
                
            print("📧 Envoi des identifiants à briceouabo@gmail.com...")
            
            action_type = "réinitialisé" if is_reset else "généré"
            subject_prefix = "🔄 Mot de passe réinitialisé" if is_reset else "🔐 Accès Admin Initial"
            
            email_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject_prefix} - Wendogo</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1f2937 0%, #111827 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                    <h1 style="margin: 0 0 10px 0; font-size: 28px;">🔐 Wendogo Admin</h1>
                    <p style="margin: 0; opacity: 0.9; font-size: 16px;">Mot de passe {action_type}</p>
                </div>
                
                <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #1f2937; margin-top: 0; text-align: center;">Accès administrateur</h2>
                    
                    <div style="background: #f0fdf4; padding: 25px; border-radius: 10px; margin: 25px 0; border: 2px solid #10b981;">
                        <h3 style="color: #047857; margin-top: 0;">🔑 Informations de connexion</h3>
                        <div style="background: #f9fafb; padding: 20px; border-radius: 8px; font-family: 'Courier New', monospace; border: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 12px 0;"><strong>URL :</strong> https://wendogo.com/admin</p>
                            <p style="margin: 0 0 12px 0;"><strong>Email :</strong> admin@wendogo.com</p>
                            <p style="margin: 0;"><strong>Mot de passe :</strong> <span style="background: #fef2f2; padding: 4px 8px; border-radius: 4px; color: #dc2626; font-weight: bold;">{password}</span></p>
                        </div>
                    </div>
                    
                    <div style="background: #fffbeb; padding: 20px; border-radius: 10px; margin: 25px 0; border-left: 5px solid #f59e0b;">
                        <h3 style="color: #92400e; margin-top: 0;">⚠️ Sécurité importante</h3>
                        <ul style="color: #92400e; margin: 0; padding-left: 20px; line-height: 1.6;">
                            <li><strong>Changez ce mot de passe</strong> dès la première connexion</li>
                            <li><strong>Seul admin@wendogo.com</strong> peut accéder</li>
                            <li><strong>Supprimez cet email</strong> après utilisation</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://wendogo.com/admin" 
                           style="background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
                                  color: white; 
                                  padding: 15px 30px; 
                                  text-decoration: none; 
                                  border-radius: 8px; 
                                  font-weight: bold; 
                                  display: inline-block;">
                            🚀 Accéder à l'administration
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 25px; color: #9ca3af; font-size: 13px;">
                    <p style="margin: 0;">Mot de passe {action_type} le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=f"{subject_prefix} - Wendogo Admin",
                recipients=['briceouabo@gmail.com'],
                html=email_content
            )
            
            self.mail.send(msg)
            print("✅ Email envoyé avec succès à briceouabo@gmail.com")
            return True
            
        except Exception as e:
            print(f"❌ Erreur envoi email : {e}")
            print(f"🔑 Mot de passe à transmettre manuellement : {password}")
            return False

# Instance globale du gestionnaire
admin_manager = AdminManager()

# Fonctions d'interface pour app.py
def init_admin_system(app, db, mail):
    """Initialiser le système admin complet depuis app.py"""
    admin_manager.init_app(app, db, mail)
    
    # Créer les tables de sécurité
    with app.app_context():
        print("🛡️ Initialisation du système admin...")
        
        # Créer les tables de sécurité
        admin_manager.create_security_tables()
        
        # Créer/vérifier l'admin
        success, password, message = admin_manager.create_admin_user()
        
        if success:
            print(f"✅ {message}")
            if password:
                print(f"🔑 Mot de passe admin : {password}")
        else:
            print(f"❌ Erreur : {message}")
            
        # Vérifier la configuration
        verify_success, verify_message = admin_manager.verify_admin_setup()
        print(f"{'✅' if verify_success else '❌'} {verify_message}")

def create_admin_user():
    """Créer l'utilisateur admin - Interface simple"""
    return admin_manager.create_admin_user()

def reset_admin_password():
    """Réinitialiser le mot de passe admin - Interface simple"""
    return admin_manager.reset_admin_password()

def verify_admin():
    """Vérifier la configuration admin - Interface simple"""
    return admin_manager.verify_admin_setup()
