
from dataclasses import dataclass
from . import db

@dataclass
class ReportCard(db.Model):
    __tablename__ = 'report_card'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    lead_level_relation_id = db.Column(db.Integer, db.ForeignKey('lead_level_relation.id'), nullable=False)
    external_school_id = db.Column(db.Integer, db.ForeignKey('external_school.id'), nullable=False) # soit external_school_id soit school_id, jamais les 2 à la fois
    school_id = db.Column(db.String(8), db.ForeignKey('school.id'), nullable=False)
    mark_system_id = db.Column(db.String(8), db.ForeignKey('mark_system.id'), nullable=False)
    academic_year_organization_id = db.Column(db.String(8), db.ForeignKey('academic_year_organization.id'), nullable=False)
    subject_id = db.Column(db.String(8), db.ForeignKey('subject.id'), nullable=False) # soit subject_id soit external_subject_id, jamais les 2 à la fois
    external_subject_id = db.Column(db.Integer, db.ForeignKey('external_subject.id'), nullable=False)
    subject_weight_system_id = db.Column(db.String(8), db.ForeignKey('subject_weight_system.id'), nullable=False)
    mark = db.Column(db.Float, nullable=False)
    mark_converted = db.Column(db.Float, nullable=False) # mark converted to the mark_system of the lead target country or school
    distinction = db.Column(db.String(255), nullable=True) # ex: "Distinction", "Mention TB", "Mention B", "Mention AB", "Passable", "Fail"
    professional_experience = db.Column(db.Boolean, default=False) # True if the lead has a professional experience in this subject
    can_justify_professional_experience = db.Column(db.Boolean, default=False) # True if the lead can justify his professional experience in this subject through a certificate (attestation de stage) 
    number_of_students = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(1024), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
