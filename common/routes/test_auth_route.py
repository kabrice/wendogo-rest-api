# common/routes/test_auth_route.py
from flask import request, jsonify, current_app
from common.models.user import User
from common.models import db
import jwt
import datetime
import bcrypt

def init_routes(app):
    
    @app.route('/test/auth/info', methods=['GET'])
    def test_auth_info():
        """Test des informations d'authentification"""
        try:
            return jsonify({
                'success': True,
                'flask_running': True,
                'secret_key_configured': bool(app.config.get('SECRET_KEY')),
                'secret_key_preview': app.config.get('SECRET_KEY', 'NOT_SET')[:10] + '...' if app.config.get('SECRET_KEY') else 'NOT_SET',
                'database_connected': True,
                'current_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'jwt_test': 'OK'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/test/auth/create-test-user', methods=['POST'])
    def create_test_user():
        """Créer un utilisateur de test"""
        try:
            # Données de test
            test_email = "test@wendogo.com"
            test_password = "password123"
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter_by(email=test_email).first()
            if existing_user:
                return jsonify({
                    'success': True,
                    'message': 'Utilisateur de test existe déjà',
                    'user': {
                        'id': existing_user.id,
                        'email': existing_user.email,
                        'firstname': existing_user.firstname,
                        'lastname': existing_user.lastname
                    }
                })
            
            # Hasher le mot de passe
            hashed_password = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Créer l'utilisateur de test
            test_user = User(
                firstname='Test',
                lastname='User',
                email=test_email,
                password=hashed_password,
                provider='email',
                email_verified=True
            )
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"✅ [Flask Test] Utilisateur de test créé: {test_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Utilisateur de test créé',
                'user': {
                    'id': test_user.id,
                    'email': test_user.email,
                    'firstname': test_user.firstname,
                    'lastname': test_user.lastname
                },
                'credentials': {
                    'email': test_email,
                    'password': test_password
                }
            })
            
        except Exception as e:
            print(f"❌ [Flask Test] Erreur création utilisateur: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/test/auth/login', methods=['POST'])
    def test_login():
        """Test de connexion avec logs détaillés"""
        data = request.json
        
        try:
            email = data.get('email')
            password = data.get('password')
            
            print(f"🔍 [Flask Test] Tentative de connexion: {email}")
            print(f"🔍 [Flask Test] Password reçu: {password}")
            
            if not email or not password:
                return jsonify({
                    'success': False, 
                    'error': 'Email et mot de passe requis',
                    'received_data': data
                }), 400
            
            # Chercher l'utilisateur
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ [Flask Test] Utilisateur non trouvé: {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Utilisateur non trouvé',
                    'email_searched': email
                }), 401
            
            print(f"✅ [Flask Test] Utilisateur trouvé: {user.id}")
            
            # Vérifier le mot de passe
            if not user.password:
                print(f"❌ [Flask Test] Pas de mot de passe défini pour: {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Pas de mot de passe défini'
                }), 401
            
            # Vérification mot de passe
            try:
                password_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
                print(f"🔍 [Flask Test] Vérification mot de passe: {password_valid}")
            except Exception as e:
                print(f"❌ [Flask Test] Erreur vérification mot de passe: {e}")
                password_valid = False
            
            if not password_valid:
                print(f"❌ [Flask Test] Mot de passe incorrect pour: {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Mot de passe incorrect'
                }), 401
            
            # Vérifier email vérifié
            if not user.email_verified:
                print(f"⚠️ [Flask Test] Email non vérifié pour: {email}")
                return jsonify({
                    'success': False, 
                    'error': 'Email non vérifié',
                    'error_code': 'EMAIL_NOT_VERIFIED'
                }), 403
            
            print(f"✅ [Flask Test] Authentification réussie pour: {email}")
            
            # Générer JWT token avec logs détaillés
            try:
                secret_key = app.config.get('SECRET_KEY', 'fallback-secret')
                print(f"🔍 [Flask Test] Secret key utilisée: {secret_key[:10]}...")
                
                token_payload = {
                    'user_id': user.id,
                    'email': user.email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
                }
                print(f"🔍 [Flask Test] Payload token: {token_payload}")
                
                token = jwt.encode(token_payload, secret_key, algorithm='HS256')
                print(f"✅ [Flask Test] Token généré: {token[:50]}...")
                
                # Test de décodage immédiat
                decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
                print(f"✅ [Flask Test] Token décodé avec succès: {decoded}")
                
            except Exception as e:
                print(f"❌ [Flask Test] Erreur génération JWT: {e}")
                token = None
            
            # Préparer la réponse
            response_data = {
                'success': True,
                'message': 'Connexion réussie',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'avatar_url': user.avatar_url,
                    'email_verified': user.email_verified,
                    'provider': user.provider
                },
                'token': token,
                'token_info': {
                    'present': bool(token),
                    'length': len(token) if token else 0,
                    'preview': token[:50] + '...' if token else None
                }
            }
            
            print(f"✅ [Flask Test] Réponse préparée - Token présent: {bool(token)}")
            return jsonify(response_data)
            
        except Exception as e:
            print(f"❌ [Flask Test] Erreur login: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'error': 'Erreur serveur',
                'details': str(e)
            }), 500

    @app.route('/test/auth/oauth-signin', methods=['POST'])
    def test_oauth_signin():
        """Test de connexion OAuth avec logs détaillés"""
        data = request.json
        
        try:
            provider = data.get('provider')
            provider_id = data.get('provider_id', 'test_provider_id')
            email = data.get('email')
            firstname = data.get('firstname', 'Test')
            lastname = data.get('lastname', 'User')
            avatar_url = data.get('avatar_url')
            
            print(f"🔍 [Flask Test] OAuth signin: {provider} - {email}")
            
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
                print(f"✅ [Flask Test] Utilisateur OAuth trouvé: {user.id}")
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
                print(f"🔍 [Flask Test] Création nouvel utilisateur OAuth")
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
            print(f"✅ [Flask Test] Utilisateur OAuth sauvegardé: {user.id}")
            
            # Générer JWT token
            try:
                token = jwt.encode({
                    'user_id': user.id,
                    'email': user.email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)
                }, app.config['SECRET_KEY'], algorithm='HS256')
                
                print(f"✅ [Flask Test] Token OAuth généré: {token[:50]}...")
                
            except Exception as e:
                print(f"❌ [Flask Test] Erreur génération JWT OAuth: {e}")
                token = None
            
            response_data = {
                'success': True,
                'message': 'OAuth connexion réussie',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'avatar_url': user.avatar_url,
                    'provider': user.provider
                },
                'token': token,
                'token_info': {
                    'present': bool(token),
                    'length': len(token) if token else 0,
                    'preview': token[:50] + '...' if token else None
                }
            }
            
            print(f"✅ [Flask Test] Réponse OAuth préparée - Token présent: {bool(token)}")
            return jsonify(response_data)
            
        except Exception as e:
            print(f"❌ [Flask Test] Erreur OAuth signin: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'error': str(e)
            }), 500

    @app.route('/test/auth/verify-token', methods=['POST'])
    def test_verify_token():
        """Test de vérification d'un token JWT"""
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token manquant'
            }), 400
        
        try:
            # Décoder le token
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Vérifier l'utilisateur
            user = User.query.get(decoded['user_id'])
            
            return jsonify({
                'success': True,
                'token_valid': True,
                'decoded_payload': decoded,
                'user_exists': bool(user),
                'user_info': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname
                } if user else None
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'token_valid': False,
                'error': 'Token expiré'
            }), 401
        except jwt.InvalidTokenError as e:
            return jsonify({
                'success': False,
                'token_valid': False,
                'error': 'Token invalide',
                'details': str(e)
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
