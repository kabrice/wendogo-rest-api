from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class AdminSession(db.Model):
    __tablename__ = 'admin_sessions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token_id = db.Column(db.String(255), unique=True, nullable=False)
    
    # Informations de connexion
    ip_address = db.Column(db.String(45), nullable=False)  # Support IPv6
    user_agent = db.Column(db.Text, nullable=True)
    
    # Gestion de la session
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=db.func.current_timestamp())
    logged_out_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    user = db.relationship('User', backref=db.backref('admin_sessions', lazy=True))

    def __init__(self, user_id, token_id, ip_address, user_agent, expires_at, **kwargs):
        self.user_id = user_id
        self.token_id = token_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.expires_at = expires_at
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.last_activity = kwargs.get('last_activity', datetime.utcnow())
        self.is_active = kwargs.get('is_active', True)

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token_id': self.token_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'logged_out_at': self.logged_out_at.isoformat() if self.logged_out_at else None,
            'is_active': self.is_active
        }

    def is_expired(self):
        """Vérifier si la session est expirée"""
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f'<AdminSession {self.id}: User {self.user_id} - {self.ip_address}>'

