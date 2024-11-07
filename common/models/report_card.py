
from dataclasses import dataclass
from . import db

@dataclass
class ReportCard(db.Model):
    """Report card header of the student for a specific school year"""
    __tablename__ = 'report_card'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    school_year_id = db.Column(db.String(8), db.ForeignKey('school_year.id'), nullable=False)
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=False)
    #level = db.Column(db.Integer, nullable=False) # 3  = Bulletin de note le plus récent, 2 = Bulletin de note de l'année n-2, 1 = Bulletin de note de l'année n-1
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    external_school_id = db.Column(db.Integer, db.ForeignKey('external_school.id'), nullable=False) # school name entered by the user different from the built-in school (school object)
    spoken_language_id = db.Column(db.String(8), db.ForeignKey('spoken_language.id'), nullable=False)
    academic_year_organization_id = db.Column(db.String(8), db.ForeignKey('academic_year_organization.id'), nullable=False) # ayo00001 => Trimestre, ayo00002 => Semestre
    mark_system_id = db.Column(db.String(8), db.ForeignKey('mark_system.id'), nullable=False) # crs0001 => Sur 6, crs0002 => Sur 10, crs0003 => Sur 20, crs0004 => Sur 100, crs0005 => Lettres (A+, A, B-, etc.)
    subject_weight_system_id = db.Column(db.String(8), db.ForeignKey('subject_weight_system.id'), nullable=False)  # sws001 => Coefficient, sws002 => Crédit
    school_term1_average_mark_in_20 = db.Column(db.Float, nullable=False) # Moyenne générale sur 20 du school_term 1 (semestre 1 ou trimestre 1)
    school_term2_average_mark_in_20 = db.Column(db.Float, nullable=False) # Moyenne générale sur 20 du school_term 2 (semestre 2 ou trimestre 2)
    school_term3_average_mark_in_20 = db.Column(db.Float, nullable=False) # Moyenne générale sur 20 du school_term 3 (trimestre 3)
    baccalaureat_average_mark_in_20 = db.Column(db.Float, nullable=False) # Moyenne générale sur 20 du baccalaureat
    average_mark_in_20 = db.Column(db.Float, nullable=False) # Moyenne générale sur 20 de l'année scolaire
    school_term1_overall_rank = db.Column(db.Integer, nullable=False) # lead overall rank for the school_term 1 (semestre 1 ou trimestre 1)
    school_term2_overall_rank = db.Column(db.Integer, nullable=False) # lead overall rank for the school_term 2 (semestre 2 ou trimestre 2)
    school_term3_overall_rank = db.Column(db.Integer, nullable=False) # lead overall rank for the school_term 3 (trimestre 3)
    overall_rank = db.Column(db.Integer, nullable=False) # lead overall rank in the class based on then rank of the student in each subject
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    school_year = db.relationship('SchoolYear', backref='report_card')
    bac = db.relationship('Bac', backref='report_card')
    lead = db.relationship('Lead', backref='report_card')
    country = db.relationship('Countries', backref='report_card')
    city = db.relationship('Cities', backref='report_card')
    external_school = db.relationship('ExternalSchool', backref='report_card')
    spoken_language = db.relationship('SpokenLanguage', backref='report_card')
    academic_year_organization = db.relationship('AcademicYearOrganization', backref='report_card')
    mark_system = db.relationship('MarkSystem', backref='report_card')

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
