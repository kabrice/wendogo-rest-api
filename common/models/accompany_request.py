from dataclasses import dataclass
from datetime import datetime
from . import db

@dataclass
class AccompanyRequest(db.Model):
    __tablename__ = 'accompany_requests'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Détails de l'offre
    offer_id = db.Column(db.String(50), nullable=False)  # 'orientation', 'visa', 'installation'
    offer_name = db.Column(db.String(255), nullable=False)  # Nom de l'offre
    price = db.Column(db.Float, nullable=False)  # Prix en EUR
    currency = db.Column(db.String(10), default='EUR')  # Devise utilisateur
    
    # Détails du projet
    project_description = db.Column(db.Text, nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    
    # Préférences de contact
    preferred_contact = db.Column(db.String(20), default='email')  # 'email', 'whatsapp', 'phone'
    urgency = db.Column(db.String(20), default='normal')  # 'normal', 'urgent', 'very_urgent'
    
    # Statut et suivi
    status = db.Column(db.String(20), default='pending')  # 'pending', 'contacted', 'in_progress', 'completed', 'cancelled'
    assigned_counselor = db.Column(db.String(255), nullable=True)  # Nom du conseiller assigné
    notes = db.Column(db.Text, nullable=True)  # Notes internes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    contacted_at = db.Column(db.DateTime, nullable=True)  # Date de premier contact
    
    # ✅ CORRECTION: Relation explicite sans backref pour éviter les conflits
    user = db.relationship('User', foreign_keys=[user_id], back_populates='accompany_requests')

    def __init__(self, user_id, offer_id, offer_name, price, project_description, **kwargs):
        self.user_id = user_id
        self.offer_id = offer_id
        self.offer_name = offer_name
        self.price = price
        self.project_description = project_description
        self.currency = kwargs.get('currency', 'EUR')
        self.additional_info = kwargs.get('additional_info')
        self.preferred_contact = kwargs.get('preferred_contact', 'email')
        self.urgency = kwargs.get('urgency', 'normal')
        self.status = kwargs.get('status', 'pending')

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'offer_id': self.offer_id,
            'offer_name': self.offer_name,
            'price': self.price,
            'currency': self.currency,
            'project_description': self.project_description,
            'additional_info': self.additional_info,
            'preferred_contact': self.preferred_contact,
            'urgency': self.urgency,
            'status': self.status,
            'assigned_counselor': self.assigned_counselor,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contacted_at': self.contacted_at.isoformat() if self.contacted_at else None
        }

    def get_status_label(self):
        """Retourne le libellé du statut en français"""
        status_labels = {
            'pending': 'En attente',
            'contacted': 'Contacté',
            'in_progress': 'En cours',
            'completed': 'Terminé',
            'cancelled': 'Annulé'
        }
        return status_labels.get(self.status, self.status)

    def get_urgency_label(self):
        """Retourne le libellé d'urgence en français"""
        urgency_labels = {
            'normal': 'Normal',
            'urgent': 'Urgent',
            'very_urgent': 'Très urgent'
        }
        return urgency_labels.get(self.urgency, self.urgency)

    def __repr__(self):
        return f'<AccompanyRequest {self.id}: {self.offer_name} - User {self.user_id}>'
