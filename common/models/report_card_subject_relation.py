
from dataclasses import dataclass
from . import db

@dataclass
class ReportCardSubjectRelation(db.Model):
    """Sort of subject and the caracteristics of the mark for a report card."""
    __tablename__ = 'report_card_subject_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    report_card_id = db.Column(db.Integer, db.ForeignKey('report_card.id'), nullable=False)
    school_term = db.Column(db.Integer, nullable=False) # n° de trimestre ou de semestre (report_card.academic_year_organization_id) : 1=>Trimestre 1, 2=>Trimestre 2, 3=>Trimestre 3 
                                                       # or 1=>Semestre 1, 2=>Semestre 2 when is_baccalaureat = False. If is_baccalaureat = True, we ignore this field
    mark = db.Column(db.String(4), nullable=False) # mark in the mark_system of the country where the mark was obtained
    mark_in_20 = db.Column(db.Float, nullable=False) # mark converted to the 20 mark system of the lead target country or school
    weight = db.Column(db.Float, nullable=False) # Credit ou coefficient value of the subject
    rank = db.Column(db.Integer, nullable=False) # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 : 1 => meilleur note, 10 => moins bonne note
    external_subject_id = db.Column(db.Integer, db.ForeignKey('external_subject.id'), nullable=False) # external subject entered by the user different from the built-in 
                                                                                                      # subject (subject object) recognized by the system
    subject_id = db.Column(db.String(8), db.ForeignKey('subject.id'), nullable=False) # use this when the subject is recognized by the system
    is_baccalaureat = db.Column(db.Boolean, nullable=False, default=False) # True if the subject is a baccalaureat subject
    is_pratical_subject = db.Column(db.Boolean, nullable=False, default=False) # TP: Travaux Pratiques
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    external_subject = db.relationship('ExternalSubject', backref='report_card_subject_relation', lazy=True)
    subject = db.relationship('Subject', backref='report_card_subject_relation', lazy=True)
    report_card = db.relationship('ReportCard', backref='report_card_subject_relation', lazy=True)

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
