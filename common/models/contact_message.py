# common/models/contact_message.py - Modèle pour les messages de contact

from dataclasses import dataclass
from . import db

@dataclass
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    
    # Informations de contact
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Type de projet
    project_type = db.Column(db.Enum(
        'orientation', 
        'visa', 
        'campus-france', 
        'parcoursup', 
        'logement', 
        'general', 
        'other',
        name='project_type_enum'
    ), nullable=False, default='general')
    
    # Statut et suivi
    status = db.Column(db.Enum(
        'new', 
        'read', 
        'replied', 
        'archived',
        name='contact_status_enum'
    ), nullable=False, default='new')
    
    assigned_to = db.Column(db.String(255), nullable=True)  # Admin qui s'occupe du message
    admin_notes = db.Column(db.Text, nullable=True)  # Notes internes
    
    # Métadonnées techniques
    ip_address = db.Column(db.String(45), nullable=True)  # Support IPv4 et IPv6
    user_agent = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    replied_at = db.Column(db.DateTime, nullable=True)  # Date de réponse
    read_at = db.Column(db.DateTime, nullable=True)  # Date de première lecture

    def __init__(self, name, email, subject, message, project_type='general', **kwargs):
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
        self.project_type = project_type
        self.status = kwargs.get('status', 'new')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.assigned_to = kwargs.get('assigned_to')
        self.admin_notes = kwargs.get('admin_notes')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'project_type': self.project_type,
            'status': self.status,
            'status_label': self.get_status_label(),
            'project_type_label': self.get_project_type_label(),
            'assigned_to': self.assigned_to,
            'admin_notes': self.admin_notes,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_new': self.status == 'new',
            'is_urgent': self.is_urgent_project(),
            'response_time': self.get_response_time()
        }

    def get_status_label(self):
        """Retourne le libellé du statut en français"""
        status_labels = {
            'new': 'Nouveau',
            'read': 'Lu',
            'replied': 'Répondu',
            'archived': 'Archivé'
        }
        return status_labels.get(self.status, self.status)

    def get_project_type_label(self):
        """Retourne le libellé du type de projet en français"""
        project_labels = {
            'orientation': 'Orientation et formations',
            'visa': 'Visa étudiant',
            'campus-france': 'Campus France',
            'parcoursup': 'Parcoursup',
            'logement': 'Logement étudiant',
            'general': 'Question générale',
            'other': 'Autre'
        }
        return project_labels.get(self.project_type, self.project_type)

    def get_project_type_icon(self):
        """Retourne l'icône associée au type de projet"""
        project_icons = {
            'orientation': '🎓',
            'visa': '📋',
            'campus-france': '🏛️',
            'parcoursup': '📚',
            'logement': '🏠',
            'general': '❓',
            'other': '📝'
        }
        return project_icons.get(self.project_type, '📝')

    def is_urgent_project(self):
        """Détermine si le type de projet est urgent"""
        urgent_projects = ['visa', 'campus-france', 'parcoursup']
        return self.project_type in urgent_projects

    def get_response_time(self):
        """Calcule le temps de réponse en heures"""
        if not self.replied_at or not self.created_at:
            return None
        
        delta = self.replied_at - self.created_at
        hours = delta.total_seconds() / 3600
        return round(hours, 1)

    def mark_as_read(self, admin_email=None):
        """Marque le message comme lu"""
        if self.status == 'new':
            self.status = 'read'
            self.read_at = db.func.current_timestamp()
            if admin_email:
                self.assigned_to = admin_email
            db.session.commit()

    def mark_as_replied(self, admin_email=None, add_note=None):
        """Marque le message comme répondu"""
        self.status = 'replied'
        self.replied_at = db.func.current_timestamp()
        if admin_email:
            self.assigned_to = admin_email
        if add_note:
            current_notes = self.admin_notes or ""
            timestamp = db.func.current_timestamp()
            self.admin_notes = f"{current_notes}\n[{timestamp}] Répondu par {admin_email}: {add_note}"
        db.session.commit()

    def archive(self, admin_email=None, reason=None):
        """Archive le message"""
        self.status = 'archived'
        if admin_email:
            self.assigned_to = admin_email
        if reason:
            current_notes = self.admin_notes or ""
            timestamp = db.func.current_timestamp()
            self.admin_notes = f"{current_notes}\n[{timestamp}] Archivé par {admin_email}: {reason}"
        db.session.commit()

    def add_admin_note(self, admin_email, note):
        """Ajoute une note admin"""
        current_notes = self.admin_notes or ""
        timestamp = db.func.current_timestamp()
        self.admin_notes = f"{current_notes}\n[{timestamp}] {admin_email}: {note}"
        db.session.commit()

    @staticmethod
    def get_stats():
        """Retourne les statistiques des messages"""
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(ContactMessage.id).label('total_messages'),
            func.count(case([(ContactMessage.status == 'new', 1)])).label('new_messages'),
            func.count(case([(ContactMessage.status == 'read', 1)])).label('read_messages'),
            func.count(case([(ContactMessage.status == 'replied', 1)])).label('replied_messages'),
            func.count(case([(ContactMessage.status == 'archived', 1)])).label('archived_messages'),
            func.count(case([(func.date(ContactMessage.created_at) == func.curdate(), 1)])).label('today_messages'),
            func.count(case([(ContactMessage.created_at >= func.date_sub(func.now(), text('INTERVAL 7 DAY')), 1)])).label('week_messages')
        ).first()
        
        return {
            'total_messages': stats.total_messages or 0,
            'new_messages': stats.new_messages or 0,
            'read_messages': stats.read_messages or 0,
            'replied_messages': stats.replied_messages or 0,
            'archived_messages': stats.archived_messages or 0,
            'today_messages': stats.today_messages or 0,
            'week_messages': stats.week_messages or 0
        }

    @staticmethod
    def get_project_type_breakdown():
        """Retourne la répartition par type de projet"""
        from sqlalchemy import func
        
        breakdown = db.session.query(
            ContactMessage.project_type,
            func.count(ContactMessage.id).label('count')
        ).group_by(ContactMessage.project_type).all()
        
        return [
            {
                'project_type': item.project_type,
                'count': item.count,
                'label': ContactMessage().get_project_type_label() if hasattr(ContactMessage(), 'get_project_type_label') else item.project_type,
                'icon': ContactMessage().get_project_type_icon() if hasattr(ContactMessage(), 'get_project_type_icon') else '📝'
            }
            for item in breakdown
        ]

    @staticmethod
    def get_recent_messages(limit=10):
        """Retourne les messages récents"""
        return ContactMessage.query.order_by(
            ContactMessage.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_unread_count():
        """Retourne le nombre de messages non lus"""
        return ContactMessage.query.filter(
            ContactMessage.status.in_(['new', 'read'])
        ).count()

    def __repr__(self):
        return f'<ContactMessage {self.id}: {self.name} - {self.subject[:50]}>'
