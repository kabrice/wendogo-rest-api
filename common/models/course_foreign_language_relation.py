
from dataclasses import dataclass
from . import db

@dataclass
class CourseForeignLanguageRelation(db.Model):
    "Niveau de langue étrangère exigée pour une formation donnée."

    __tablename__ = 'course_foreign_language_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    external_id = db.Column(db.Integer, autoincrement=True)
    course_id = db.Column(db.String(8), db.ForeignKey('course.id'), nullable=False)
    foreign_language_id = db.Column(db.String(8), db.ForeignKey('foreign_language.id'), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(15), nullable=False) # A1, A2, B1, B2, C1, C2
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
