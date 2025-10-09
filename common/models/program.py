from dataclasses import dataclass
from . import db

@dataclass
class Program(db.Model):
    """Programme d'études proposé par une école/université."""
    __tablename__ = 'program'
    __table_args__ = {'extend_existing': True} 

    # Identifiants principaux
    id = db.Column(db.String(10), primary_key=True)
    school_id = db.Column(db.String(8), db.ForeignKey('school.id'), nullable=False)
    school_name = db.Column(db.String(255), nullable=False)
    eef_name = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Description et détails du programme
    description = db.Column(db.Text, nullable=True)
    desired_profiles = db.Column(db.Text, nullable=True)  # AJOUTÉ - manquait dans votre modèle
    curriculum_highlights = db.Column(db.Text, nullable=True)
    skills_acquired = db.Column(db.Text, nullable=True)
    special_comment = db.Column(db.Text, nullable=True)
    
    # Durée et organisation
    fi_school_duration = db.Column(db.String(50), nullable=True)
    fi_duration_comment = db.Column(db.Text, nullable=True)
    ca_school_duration = db.Column(db.String(50), nullable=True)
    ca_program_details = db.Column(db.Text, nullable=True)
    
    # Candidatures et admissions
    application_date = db.Column(db.String(100), nullable=True)
    application_date_comment = db.Column(db.Text, nullable=True)
    intake = db.Column(db.String(100), nullable=True)
    intake_comment = db.Column(db.Text, nullable=True)
    intake_capacity = db.Column(db.Integer, nullable=True)
    url_application = db.Column(db.String(500), nullable=True)
    
    # Domaines et certifications
    sub_domain1_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)
    sub_domain2_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)
    sub_domain3_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)
    state_certification_type = db.Column(db.String(100), nullable=True)
    state_certification_type_complement = db.Column(db.String(255), nullable=True)
    state_certification_type_complement2 = db.Column(db.String(255), nullable=True)
    
    # Niveau et grade
    rncp_level = db.Column(db.Integer, nullable=True)
    rncp_certifier = db.Column(db.String(255), nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    
    # Partenariats et doubles diplômes
    joint_preparation_with = db.Column(db.Text, nullable=True)
    degree_issuer = db.Column(db.String(255), nullable=True)
    dual_degree_with = db.Column(db.Text, nullable=True)
    international_double_degree = db.Column(db.Text, nullable=True)
    
    # Alternance et apprentissage
    apprenticeship_manager = db.Column(db.String(255), nullable=True)
    
    # Frais de scolarité
    fi_registration_fee = db.Column(db.String(100), nullable=True)
    fi_annual_tuition_fee = db.Column(db.String(100), nullable=True)
    tuition_comment = db.Column(db.Text, nullable=True)
    tuition = db.Column(db.String(100), nullable=True)
    
    # FRAIS PAR ANNÉE - INT(10) dans la base
    y1_tuition = db.Column(db.Integer, nullable=True)
    y2_tuition = db.Column(db.Integer, nullable=True)
    y3_tuition = db.Column(db.Integer, nullable=True)
    y4_tuition = db.Column(db.Integer, nullable=True)
    y5_tuition = db.Column(db.Integer, nullable=True)
    
    first_deposit_comment = db.Column(db.Text, nullable=True)
    first_deposit = db.Column(db.String(100), nullable=True)
    
    # Admissions par année - Année 1
    y1_required_level = db.Column(db.String(50), nullable=True)
    required_degree1 = db.Column(db.String(255), nullable=True)
    y1_admission_details = db.Column(db.Text, nullable=True)
    y1_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level1 = db.Column(db.String(50), nullable=True)
    
    # Année 2
    y2_required_level = db.Column(db.String(50), nullable=True)
    required_degree2 = db.Column(db.String(255), nullable=True)
    y2_admission_details = db.Column(db.Text, nullable=True)
    y2_admission_method = db.Column(db.String(255), nullable=True)
    y2_application_date = db.Column(db.String(100), nullable=True)
    y2_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level2 = db.Column(db.String(50), nullable=True)
    
    # Année 3
    y3_required_level = db.Column(db.String(50), nullable=True)
    required_degree3 = db.Column(db.String(255), nullable=True)
    y3_required_degree = db.Column(db.String(255), nullable=True)  # A supprimer
    y3_admission_method = db.Column(db.String(255), nullable=True)
    y3_admission_details = db.Column(db.Text, nullable=True)
    y3_application_date = db.Column(db.String(100), nullable=True)
    y3_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level3 = db.Column(db.String(50), nullable=True)
    y3_admission_by_exam = db.Column(db.String(255), nullable=True)
    
    # Année 4
    y4_required_level = db.Column(db.String(50), nullable=True)
    required_degree4 = db.Column(db.String(255), nullable=True)
    y4_admission_method = db.Column(db.String(255), nullable=True)
    y4_admission_details = db.Column(db.Text, nullable=True)
    y4_application_date = db.Column(db.String(100), nullable=True)
    y4_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level4 = db.Column(db.String(50), nullable=True)
    
    # Année 5
    y5_required_level = db.Column(db.String(50), nullable=True)
    y5_required_degree = db.Column(db.String(255), nullable=True)  # A supprimer
    y5_admission_method = db.Column(db.String(255), nullable=True)
    y5_application_date = db.Column(db.String(100), nullable=True)
    required_degree5 = db.Column(db.String(255), nullable=True)
    y5_admission_details = db.Column(db.Text, nullable=True)
    y5_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level5 = db.Column(db.String(50), nullable=True)
    
    # SEO et marketing
    seo_title = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.Text, nullable=True)
    seo_keywords = db.Column(db.Text, nullable=True)
    
    # Statistiques et résultats
    careers = db.Column(db.Text, nullable=True)
    corporate_partners = db.Column(db.Text, nullable=True)
    employment_rate_among_graduates = db.Column(db.String(100), nullable=True)
    success_rate_of_the_program = db.Column(db.String(100), nullable=True)
    starting_salary = db.Column(db.String(100), nullable=True)
    
    # Métadonnées système
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # Campus France et évaluations
    parallel_procedure = db.Column(db.Boolean, nullable=False, default=False)
    bienvenue_en_france_level = db.Column(db.Integer, nullable=True)
    contact = db.Column(db.Text, nullable=True)
    language_tech_level_unofficial1 = db.Column(db.String(50), nullable=True)
    language_tech_level_unofficial2 = db.Column(db.String(50), nullable=True)
    language_tech_level_unofficial3 = db.Column(db.String(50), nullable=True)
    language_tech_level_unofficial4 = db.Column(db.String(50), nullable=True)
    language_tech_level_unofficial5 = db.Column(db.String(50), nullable=True)
    is_referenced_in_eef = db.Column(db.Boolean, nullable=False, default=False)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    
    # Relations
    school = db.relationship('School', backref=db.backref('programs', lazy=True))
    sub_domain1 = db.relationship('Subdomain', foreign_keys=[sub_domain1_id], backref='programs_as_subdomain1')
    sub_domain2 = db.relationship('Subdomain', foreign_keys=[sub_domain2_id], backref='programs_as_subdomain2')  
    sub_domain3 = db.relationship('Subdomain', foreign_keys=[sub_domain3_id], backref='programs_as_subdomain3')

    def as_dict(self):
        """Convertit l'objet en dictionnaire, excluant les champs sensibles"""
        excluded_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
    
    def as_dict_with_subdomains(self):
        """Convertit l'objet en dictionnaire avec les noms des sous-domaines"""
        data = self.as_dict()
        
        if self.sub_domain1:
            data['sub_domain1_name'] = self.sub_domain1.name
        if self.sub_domain2:
            data['sub_domain2_name'] = self.sub_domain2.name
        if self.sub_domain3:
            data['sub_domain3_name'] = self.sub_domain3.name
            
        return data
    
    def as_dict_admission(self):
        """Convertit l'objet en dictionnaire focalisé sur l'admission"""
        admission_fields = [
            'id', 'name', 'school_name', 'description', 'slug',
            'application_date', 'intake', 'intake_capacity',
            'y1_required_level', 'required_degree1', 'y1_admission_details',
            'y2_required_level', 'required_degree2', 'y2_admission_details',
            'y3_required_level', 'required_degree3', 'y3_admission_details',
            'y4_required_level', 'required_degree4', 'y4_admission_details',
            'y5_required_level', 'required_degree5', 'y5_admission_details',
            'tuition', 'first_deposit', 'url_application',
            'y1_teaching_language_with_required_level',
            'y1_tuition', 'y2_tuition', 'y3_tuition', 'y4_tuition', 'y5_tuition'
        ]
        return {field: getattr(self, field) for field in admission_fields if hasattr(self, field)}
    
    def as_dict_career(self):
        """Convertit l'objet en dictionnaire focalisé sur les débouchés"""
        career_fields = [
            'id', 'name', 'school_name', 'description', 'slug',
            'careers', 'corporate_partners', 'employment_rate_among_graduates',
            'success_rate_of_the_program', 'starting_salary',
            'skills_acquired', 'curriculum_highlights'
        ]
        return {field: getattr(self, field) for field in career_fields if hasattr(self, field)}
    
    def as_dict_full(self):
        """Convertit l'objet en dictionnaire complet (pour admin)"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Program {self.id}: {self.name} ({self.school_name})>'
