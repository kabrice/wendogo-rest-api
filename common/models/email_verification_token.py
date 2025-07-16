from dataclasses import dataclass
from . import db

# Nouveau modèle pour les tokens de vérification
@dataclass
class EmailVerificationToken(db.Model):
    __tablename__ = 'email_verification_token'
    __table_args__ = {'extend_existing': True} 


    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, email, token, expires_at):
        self.email = email
        self.token = token
        self.expires_at = expires_at
        self.used = False

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used,
            'created_at': self.created_at.isoformat()
        }
    