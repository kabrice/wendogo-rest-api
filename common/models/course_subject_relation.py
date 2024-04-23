
from dataclasses import dataclass

from . import db

@dataclass
class CourseSubjectRelation(db.Model):
    "Matière exigée pour une formation donnée"

    __tablename__ = 'course_subject_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(8), db.ForeignKey('course.id'), nullable=False)
    subject_id = db.Column(db.String(8), db.ForeignKey('subject.id'), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(15), nullable=False)
    check_professional_experience = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
