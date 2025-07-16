
# common/models/security_log.py - Modèle pour les logs de sécurité
from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class SecurityLog(db.Model):
    __tablename__ = 'security_logs'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    
    # Type d'événement de sécurité
    event_type = db.Column(db.String(100), nullable=False)  # 'login_attempt', 'unauthorized_access', etc.
    
    # Informations de connexion
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    
    # Données additionnelles (JSON)
    additional_data = db.Column(db.JSON, nullable=True)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Niveau de sévérité
    severity = db.Column(db.String(20), default='INFO')  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

    def __init__(self, event_type, ip_address, user_agent=None, additional_data=None, **kwargs):
        self.event_type = event_type
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.additional_data = additional_data or {}
        self.timestamp = kwargs.get('timestamp', datetime.utcnow())
        self.severity = kwargs.get('severity', 'INFO')

    def as_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'additional_data': self.additional_data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'severity': self.severity
        }

    def __repr__(self):
        return f'<SecurityLog {self.id}: {self.event_type} from {self.ip_address}>'
