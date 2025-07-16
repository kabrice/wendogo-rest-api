
# common/models/organization_contact.py - INCHANGÉ, pas de problème de relation

from dataclasses import dataclass
from . import db

@dataclass
class OrganizationContact(db.Model):
    __tablename__ = 'organization_contacts'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de contact
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(255), nullable=False)  # Intitulé du poste
    organization = db.Column(db.String(255), nullable=False)  # Nom de l'établissement
    email = db.Column(db.String(255), nullable=False)
    
    # Message et suivi
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # 'new', 'contacted', 'in_discussion', 'partner', 'rejected'
    assigned_to = db.Column(db.String(255), nullable=True)  # Qui s'occupe du dossier
    notes = db.Column(db.Text, nullable=True)  # Notes internes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    contacted_at = db.Column(db.DateTime, nullable=True)  # Date de premier contact

    def __init__(self, first_name, last_name, position, organization, email, message, **kwargs):
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.organization = organization
        self.email = email
        self.message = message
        self.status = kwargs.get('status', 'new')

    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f"{self.first_name} {self.last_name}",
            'position': self.position,
            'organization': self.organization,
            'email': self.email,
            'message': self.message,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contacted_at': self.contacted_at.isoformat() if self.contacted_at else None
        }

    def get_status_label(self):
        """Retourne le libellé du statut en français"""
        status_labels = {
            'new': 'Nouveau',
            'contacted': 'Contacté',
            'in_discussion': 'En discussion',
            'partner': 'Partenaire',
            'rejected': 'Refusé'
        }
        return status_labels.get(self.status, self.status)

    def __repr__(self):
        return f'<OrganizationContact {self.id}: {self.organization} - {self.first_name} {self.last_name}>'
