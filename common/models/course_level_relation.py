
from dataclasses import dataclass
from . import db

@dataclass
class CourseSubjectRelation(db.Model):
    "Niveau d'entrée conseillé pour une formation donnée."

    __tablename__ = 'course_subject_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    course_id = db.Column(db.String(8), db.ForeignKey('course.id'), nullable=False)
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=False)
    level_value_id = db.Column(db.String(8), db.ForeignKey('level_value.id'), nullable=False)
    #level_value_relation_id = db.Column(db.Integer, db.ForeignKey('level_value_relation.id'), nullable=False) # nom de la licence, master, etc.
    ranking = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
