from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class AdminPasswordReset(db.Model):
    __tablename__ = 'admin_password_resets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Token de réinitialisation
    reset_token = db.Column(db.String(255), unique=True, nullable=False)
    
    # Informations de la demande
    requested_by_email = db.Column(db.String(255), nullable=False)  # briceouabo@gmail.com
    ip_address = db.Column(db.String(45), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relations
    user = db.relationship('User', backref=db.backref('password_resets', lazy=True))

    def __init__(self, user_id, reset_token, requested_by_email, ip_address, expires_at, **kwargs):
        self.user_id = user_id
        self.reset_token = reset_token
        self.requested_by_email = requested_by_email
        self.ip_address = ip_address
        self.expires_at = expires_at
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.is_used = kwargs.get('is_used', False)

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reset_token': self.reset_token,
            'requested_by_email': self.requested_by_email,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'is_used': self.is_used
        }

    def is_expired(self):
        """Vérifier si le token est expiré"""
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self):
        """Marquer le token comme utilisé"""
        self.is_used = True
        self.used_at = datetime.utcnow()

    def __repr__(self):
        return f'<AdminPasswordReset {self.id}: User {self.user_id}>'
