
from dataclasses import dataclass
from . import db

@dataclass
class EnglishExamType(db.Model):
    """TOIEC, TOEFL, IELTS, etc."""
    __tablename__ = 'english_exam_type'
    __table_args__ = {'extend_existing': True} 
# Todo: Pas utile pour le moment
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    french_exam_score_type_id = db.Column(db.String(8), db.ForeignKey('french_exam_score_type.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
