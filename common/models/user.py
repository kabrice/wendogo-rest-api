# common/models/user.py - VERSION CORRIGÉE

from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.event import listens_for
from common.models.accompany_request import AccompanyRequest
from . import db

@dataclass
class User(db.Model):

    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(255), nullable=True)
    street = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True) 
    city = db.Column(db.String(35), nullable=True)
    description = db.Column(db.String(2500), nullable=True)
    work_description = db.Column(db.String(2500), nullable=True)
    tourism_description = db.Column(db.String(2500), nullable=True)
    family_description = db.Column(db.String(2500), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    firstname = db.Column(db.String(46), nullable=True)
    lastname = db.Column(db.String(46), nullable=True)
    birthdate = db.Column(db.Date)
    salutation = db.Column(db.String(15), nullable=True)
    country = db.Column(db.String(4), nullable=True) 
    phone = db.Column(db.String(25), nullable=True)
    has_whatsapp = db.Column(db.Boolean, unique=False, default=False, nullable=True)
    whatsapp_verification_attempt = db.Column(db.Integer, default=0)
    occupation = db.Column(db.String(20), nullable=True)
    subscription_step = db.Column(db.String(255), nullable=True)
    nationality_id = db.Column(db.String(8), db.ForeignKey('nationality.id'), nullable=True)
    passport_id = db.Column(db.Integer, db.ForeignKey('passport.id'), nullable=True)
    is_disabled = db.Column(db.Boolean, unique=False, default=False, nullable=True)
    lead_status_id = db.Column(db.String(8), db.ForeignKey('lead_status.id'), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 
    
    # Nouveaux champs pour OAuth
    google_id = db.Column(db.String(100), nullable=True, unique=True)
    facebook_id = db.Column(db.String(100), nullable=True, unique=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    provider = db.Column(db.String(20), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relations
    favorites = db.relationship('UserFavorite', backref='user', lazy=True, cascade='all, delete-orphan')    

    # Informations d'accompagnement
    has_accompany_request = db.Column(db.Boolean, default=False)
    accompany_status = db.Column(db.String(50), nullable=True)
    
    # ✅ RELATION BIDIRECTIONNELLE AVEC AccompanyRequest
    accompany_requests = db.relationship(
        'AccompanyRequest', 
        foreign_keys='AccompanyRequest.user_id',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # ✅ CONSTRUCTEUR CORRIGÉ avec tous les paramètres nécessaires
    def __init__(self, 
                 firstname='', 
                 lastname='', 
                 email='', 
                 password=None,
                 phone='',
                 birthdate=None,
                 country='',
                 salutation='', 
                 city='', 
                 occupation='', 
                 description='',
                 provider='email',
                 google_id=None,
                 facebook_id=None,
                 avatar_url=None,
                 email_verified=False,
                 has_accompany_request=False,
                 accompany_status=None,
                 **kwargs):
        """
        Constructeur du modèle User
        
        Args:
            firstname (str): Prénom
            lastname (str): Nom
            email (str): Email
            password (str): Mot de passe hashé
            phone (str): Numéro de téléphone
            birthdate (date): Date de naissance
            country (str): Code pays ISO2
            salutation (str): Titre (Mr, Mme, etc.)
            city (str): Ville
            occupation (str): Profession
            description (str): Description
            provider (str): Fournisseur d'auth ('email', 'google', 'facebook')
            google_id (str): ID Google OAuth
            facebook_id (str): ID Facebook OAuth
            avatar_url (str): URL de l'avatar
            email_verified (bool): Email vérifié
            **kwargs: Autres paramètres
        """
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.phone = phone
        self.birthdate = birthdate
        self.country = country
        self.salutation = salutation
        self.city = city
        self.occupation = occupation
        self.description = description
        self.provider = provider
        self.google_id = google_id
        self.facebook_id = facebook_id
        self.avatar_url = avatar_url
        self.email_verified = email_verified
        
        # Définir les timestamps
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.has_accompany_request = kwargs.get('has_accompany_request', False)
        self.accompany_status = kwargs.get('accompany_status')

    def as_dict(self):
        """Convertir l'objet User en dictionnaire"""
        excluded_fields = ['created_at', 'updated_at', 'whatsapp_verification_attempt', 'password']
        result = {}
        
        for field in self.__table__.c:
            if field.name not in excluded_fields:
                value = getattr(self, field.name)
                # Convertir les dates en string ISO
                if isinstance(value, datetime):
                    result[field.name] = value.isoformat()
                elif hasattr(value, 'isoformat'):  # Pour les objets date
                    result[field.name] = value.isoformat()
                else:
                    result[field.name] = value
                    
        return result

    # ✅ NOUVELLES PROPRIÉTÉS UTILITAIRES
    @property
    def latest_accompany_request(self):
        """Retourne la dernière demande d'accompagnement"""
        return self.accompany_requests.order_by(AccompanyRequest.created_at.desc()).first()
    
    @property
    def accompany_requests_count(self):
        """Retourne le nombre total de demandes d'accompagnement"""
        return self.accompany_requests.count()
    
    @property
    def pending_accompany_requests(self):
        """Retourne le nombre de demandes en attente"""
        return self.accompany_requests.filter_by(status='pending').count()
    
    @property
    def completed_accompany_requests(self):
        """Retourne le nombre de demandes terminées"""
        return self.accompany_requests.filter_by(status='completed').count()
    
    def __repr__(self):
        return f'<User {self.id}: {self.firstname} {self.lastname}>'
                
@listens_for(User, 'after_update')
def update_user_log(mapper, connection, target):
    """Mettre à jour automatiquement le timestamp updated_at"""
    user_table = User.__table__
    connection.execute(
        user_table.update().
        where(user_table.c.id==target.id).
        values(updated_at=datetime.utcnow())
    )
