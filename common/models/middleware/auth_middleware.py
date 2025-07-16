
# ═══════════════════════════════════════════════════════════
# 📁 common/middleware/auth_middleware.py (NOUVEAU)
# ═══════════════════════════════════════════════════════════

from flask import request, jsonify, g, current_app
from functools import wraps
import jwt
from common.models.user import User  # Assure the import path matches your project structure

class AuthMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.load_user)
    
    def load_user(self):
        """Charger l'utilisateur depuis le token JWT si présent"""
        g.current_user = None
        
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ')[1]
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                g.current_user = User.query.get(data['user_id'])
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
                pass
