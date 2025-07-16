from dataclasses import dataclass
from . import db

@dataclass
class Program(db.Model):
    """Programme d'études proposé par une école/université."""
    __tablename__ = 'program'
    __table_args__ = {'extend_existing': True} 

    # Identifiants principaux
    id = db.Column(db.String(10), primary_key=True)  # prog001557
    school_id = db.Column(db.String(8), db.ForeignKey('school.id'), nullable=False)  # PRIV0190
    school_name = db.Column(db.String(255), nullable=False)  # ESSCA Lyon (dénormalisé)
    name = db.Column(db.String(500), nullable=False)  # Programme Grande École ESSCA
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Description et détails du programme
    description = db.Column(db.Text, nullable=True)
    curriculum_highlights = db.Column(db.Text, nullable=True)  # Points forts du cursus
    skills_acquired = db.Column(db.Text, nullable=True)  # Compétences acquises
    special_comment = db.Column(db.Text, nullable=True)  # Commentaires spéciaux
    
    # Durée et organisation
    fi_school_duration = db.Column(db.String(50), nullable=True)  # Formation initiale - durée
    fi_duration_comment = db.Column(db.Text, nullable=True)  # Commentaire sur la durée
    ca_school_duration = db.Column(db.String(50), nullable=True)  # Contrat d'alternance - durée
    ca_program_details = db.Column(db.Text, nullable=True)  # Détails programme alternance
    
    # Candidatures et admissions
    application_date = db.Column(db.String(100), nullable=True)  # Dates de candidature
    application_date_comment = db.Column(db.Text, nullable=True)
    intake = db.Column(db.String(100), nullable=True)  # Rentrées
    intake_comment = db.Column(db.Text, nullable=True)
    intake_capacity = db.Column(db.Integer, nullable=True)  # Capacité d'accueil
    url_application = db.Column(db.String(500), nullable=True)  # URL candidature
    
    # Domaines et certifications - AVEC FOREIGN KEYS
    sub_domain1_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)  # sub0202
    sub_domain2_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)  # sub0196
    sub_domain3_id = db.Column(db.String(8), db.ForeignKey('subdomain.id'), nullable=True)  # sub0203
    state_certification_type = db.Column(db.String(100), nullable=True)  # Diplôme visé
    state_certification_type_complement = db.Column(db.String(255), nullable=True)
    state_certification_type_complement2 = db.Column(db.String(255), nullable=True)
    
    # Niveau et grade
    rncp_level = db.Column(db.Integer, nullable=True)  # Niveau RNCP (6, 7, etc.)
    rncp_certifier = db.Column(db.String(255), nullable=True)  # Organisme certificateur
    grade = db.Column(db.String(50), nullable=True)  # master, licence, etc.
    
    # Partenariats et doubles diplômes
    joint_preparation_with = db.Column(db.Text, nullable=True)  # Préparation conjointe
    degree_issuer = db.Column(db.String(255), nullable=True)  # Délivreur du diplôme
    dual_degree_with = db.Column(db.Text, nullable=True)  # Double diplôme avec
    international_double_degree = db.Column(db.Text, nullable=True)  # Double diplôme international
    
    # Alternance et apprentissage
    apprenticeship_manager = db.Column(db.String(255), nullable=True)  # Gestionnaire apprentissage
    
    # Frais de scolarité
    fi_registration_fee = db.Column(db.String(100), nullable=True)  # Frais d'inscription FI
    fi_annual_tuition_fee = db.Column(db.String(100), nullable=True)  # Frais annuels FI
    tuition_comment = db.Column(db.Text, nullable=True)  # Commentaire sur les frais
    tuition = db.Column(db.String(100), nullable=True)  # Montant principal
    first_deposit_comment = db.Column(db.Text, nullable=True)  # Commentaire acompte
    first_deposit = db.Column(db.String(100), nullable=True)  # Montant acompte
    
    # Admissions par année (Y1 à Y5)
    # Année 1
    y1_required_level = db.Column(db.String(50), nullable=True)  # bac
    required_degree1 = db.Column(db.String(255), nullable=True)  # Diplôme requis Y1
    application_details_for_year_1 = db.Column(db.Text, nullable=True)  # Détails admission Y1
    teaching_language_with_required_level_for_year_1 = db.Column(db.String(100), nullable=True)
    language_tech_level1 = db.Column(db.String(50), nullable=True)  # Fr-B2, En-B2
    
    # Année 2
    y2_required_level = db.Column(db.String(50), nullable=True)  # bac+1
    required_degree2 = db.Column(db.String(255), nullable=True)
    y2_admission_details = db.Column(db.Text, nullable=True)
    y2_admission_method = db.Column(db.String(255), nullable=True)
    y2_application_date = db.Column(db.String(100), nullable=True)
    y2_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level2 = db.Column(db.String(50), nullable=True)
    
    # Année 3
    y3_required_level = db.Column(db.String(50), nullable=True)  # bac+2
    required_degree3 = db.Column(db.String(255), nullable=True)
    y3_required_degree = db.Column(db.String(255), nullable=True)
    y3_admission_method = db.Column(db.String(255), nullable=True)
    y3_admission_details = db.Column(db.Text, nullable=True)
    y3_application_date = db.Column(db.String(100), nullable=True)
    y3_teaching_language_with_required_level = db.Column(db.String(100), nullable=True)
    language_tech_level3 = db.Column(db.String(50), nullable=True)
    y3_admission_by_exam = db.Column(db.String(255), nullable=True)
    
    # Année 4
    y4_required_level = db.Column(db.String(50), nullable=True)  # bac+3
    required_degree4 = db.Column(db.String(255), nullable=True)
    y4_admission_method = db.Column(db.String(255), nullable=True)
    y4_admission_details = db.Column(db.Text, nullable=True)
    y4_application_date = db.Column(db.String(100), nullable=True)
    teaching_language_with_required_level_for_year_4 = db.Column(db.String(100), nullable=True)
    language_tech_level4 = db.Column(db.String(50), nullable=True)
    
    # Année 5
    y5_required_level = db.Column(db.String(50), nullable=True)  # bac+4
    y5_required_degree = db.Column(db.String(255), nullable=True)
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
    careers = db.Column(db.Text, nullable=True)  # Débouchés carrière
    corporate_partners = db.Column(db.Text, nullable=True)  # Partenaires entreprises
    employment_rate_among_graduates = db.Column(db.String(100), nullable=True)  # Taux d'emploi
    success_rate_of_the_program = db.Column(db.String(100), nullable=True)  # Taux de réussite
    starting_salary = db.Column(db.String(100), nullable=True)  # Salaire de sortie
    
    # Métadonnées système
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # Programme actif
    
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
    
    # def as_dict_public(self):
    #     """Convertit l'objet en dictionnaire pour l'API publique"""
    #     if not self.is_active:
    #         return None
            
    #     excluded_fields = [
    #         'created_at', 'updated_at', 'created_by', 'updated_by',
    #         'school_id', 'is_active'
    #     ]
    #     return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
    
    def as_dict_with_subdomains(self):
        """Convertit l'objet en dictionnaire avec les noms des sous-domaines"""
        data = self.as_dict()
        
        # Ajouter les noms des sous-domaines
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
            'y1_required_level', 'required_degree1', 'application_details_for_year_1',
            'y2_required_level', 'required_degree2', 'y2_admission_details',
            'y3_required_level', 'required_degree3', 'y3_admission_details',
            'y4_required_level', 'required_degree4', 'y4_admission_details',
            'y5_required_level', 'required_degree5', 'y5_admission_details',
            'tuition', 'first_deposit', 'url_application',
            'teaching_language_with_required_level_for_year_1'
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
