from dataclasses import dataclass
from . import db

@dataclass
class School(db.Model):
    """Faculté|Institut|Ecole|UFR etc lié à l'université."""
    __tablename__ = 'school'
    __table_args__ = {'extend_existing': True} 

    # Identifiants principaux
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(255), nullable=True, unique=True, index=True)
    school_group = db.Column(db.String(255), nullable=True)
    base_city = db.Column(db.String(255), nullable=True)
    
    # Coordonnées
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Frais de scolarité et exonérations
    exoneration_tuition = db.Column(db.Integer, nullable=True)
    exoneration_tuition_comment = db.Column(db.Text, nullable=True)
    
    # Statut et accréditations
    hors_contrat = db.Column(db.Boolean, nullable=False, default=False)
    acknowledgement = db.Column(db.Text, nullable=True)
    
    # Alternance
    alternance_rate = db.Column(db.String(20), nullable=True)
    alternance_comment = db.Column(db.Text, nullable=True)
    alternance_comment_tech = db.Column(db.Text, nullable=True)
    work_study_programs = db.Column(db.Text, nullable=True)
    
    # Étudiants internationaux
    international_student_rate = db.Column(db.String(20), nullable=True)
    international_student_rate_tech = db.Column(db.String(50), nullable=True)
    international_student_comment = db.Column(db.Text, nullable=True)
    international_student_comment_tech = db.Column(db.Text, nullable=True)
    
    # Campus France
    connection_campus_france = db.Column(db.Boolean, nullable=False, default=False)
    
    # Évaluations
    rating = db.Column(db.Numeric(3, 2), nullable=True)
    reviews_counter = db.Column(db.Integer, nullable=True)
    
    # URLs et réseaux sociaux
    url = db.Column(db.String(500), nullable=True)
    facebook_url = db.Column(db.String(500), nullable=True)
    x_url = db.Column(db.String(500), nullable=True)
    linkedin_url = db.Column(db.String(500), nullable=True)
    instagram_url = db.Column(db.String(500), nullable=True)
    
    # Rankings
    national_ranking = db.Column(db.Text, nullable=True)
    international_ranking = db.Column(db.Text, nullable=True)
    
    # Support international
    international_support_before_coming = db.Column(db.Text, nullable=True)
    international_support_after_coming = db.Column(db.Text, nullable=True)
    
    # Admission et partenariats
    general_entry_requirements = db.Column(db.Text, nullable=True)
    partnerships = db.Column(db.Text, nullable=True)
    facilities = db.Column(db.Text, nullable=True)
    
    # Visibilité
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    
    # SEO
    seo_title = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.Text, nullable=True)
    seo_keywords = db.Column(db.Text, nullable=True)
    
    # Relations étrangères
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False, default=75)
    logo_path = db.Column(db.String(255), nullable=True)
    cover_page_path = db.Column(db.String(500), nullable=True)
    university_id = db.Column(db.String(8), db.ForeignKey('university.id'), nullable=True)
    
    # Métadonnées système
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    educational_language_id = db.Column(db.String(8), db.ForeignKey('spoken_language.id'), nullable=False, default='spl00002')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    
    # Relations
    university = db.relationship('University', backref=db.backref('schools', lazy=True))
    
    def as_dict(self):
        """Convertit l'objet en dictionnaire, excluant les champs sensibles"""
        excluded_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by', 
            'country_id', 'university_id', 'educational_language_id'
        ]
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
    
    def as_dict_public(self):
        """Convertit l'objet en dictionnaire pour l'API publique"""
        if not self.is_public:
            return None
            
        excluded_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by', 
            'country_id', 'university_id', 'educational_language_id',
            'email', 'phone',
            'is_public'
        ]
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
    
    def as_dict_full(self):
        """Convertit l'objet en dictionnaire complet (pour admin)"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<School {self.id}: {self.name}>'
