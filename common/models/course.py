
from dataclasses import dataclass
from . import db

@dataclass
class Course(db.Model):
    """conditions sur la specialité en question"""
    __tablename__ = 'course'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    number_of_students = db.Column(db.Integer, nullable=False)
    access_rate = db.Column(db.Float, nullable=False)
    professional_integration_rate = db.Column(db.Float, nullable=False)
    recommendation_letter_requirement_level = db.Column(db.Float, nullable=False)
    professional_experience_requirement_level = db.Column(db.Float, nullable=False)
    check_practical_work_experience = db.Column(db.Boolean, nullable=False)
    tutorial_requirement_level = db.Column(db.Float, nullable=False)
    is_progression_mandatory = db.Column(db.Boolean, nullable=False)
    is_ranking_mandatory = db.Column(db.Boolean, nullable=False)
    check_class_repeat = db.Column(db.Boolean, nullable=False)
    check_iae_score = db.Column(db.Boolean, nullable=False)
    french_level = db.Column(db.String(15), nullable=False)
    english_level = db.Column(db.String(15), nullable=False)
    exoneration_id = db.Column(db.String(8), db.ForeignKey('exoneration.id'), nullable=False)
    annual_tuition = db.Column(db.Float, nullable=False)
    check_grade_since_n3 = db.Column(db.Boolean, nullable=False)
    major_id = db.Column(db.String(8), db.ForeignKey('major.id'), nullable=False)
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    educational_language_id = db.Column(db.String(8), db.ForeignKey('educational_language.id'), nullable=False)
    comments = db.Column(db.String(1024), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
