
from dataclasses import dataclass
from . import db

@dataclass
class Course(db.Model):
    """conditions sur la specialité en question"""
    __tablename__ = 'course'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    external_id = db.Column(db.Integer, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    number_of_students = db.Column(db.Integer, nullable=True)
    access_rate = db.Column(db.Float, nullable=True)
    professional_integration_rate = db.Column(db.Float, nullable=True)
    recommendation_letter_requirement_level = db.Column(db.Float, nullable=True)
    professional_experience_requirement_level = db.Column(db.Float, nullable=True)
    check_practical_work_experience = db.Column(db.Boolean, nullable=True)
    tutorial_requirement_level = db.Column(db.Float, nullable=True)
    is_progression_mandatory = db.Column(db.Boolean, nullable=True)
    is_porfolio_mandatory = db.Column(db.Boolean, nullable=True)
    is_ranking_mandatory = db.Column(db.Boolean, nullable=True)
    check_class_repeat = db.Column(db.Boolean, nullable=True)
    check_iae_score = db.Column(db.Boolean, nullable=True)
    french_level = db.Column(db.String(15), nullable=True)
    english_level = db.Column(db.String(15), nullable=True)
    another_language_level = db.Column(db.String(15), nullable=True)
    exoneration_id = db.Column(db.String(8), db.ForeignKey('exoneration.id'), nullable=True)
    annual_tuition = db.Column(db.Float, nullable=True)
    check_grade_since_n3 = db.Column(db.Boolean, nullable=True)
    major_id = db.Column(db.String(8), db.ForeignKey('major.id'), nullable=True)
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=True)
    course_type_id = db.Column(db.String(8), db.ForeignKey('course_type.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    educational_language_id = db.Column(db.String(8), db.ForeignKey('educational_language.id'), nullable=True)
    comments = db.Column(db.String(1024), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
