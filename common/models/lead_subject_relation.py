
from dataclasses import dataclass
from . import db

@dataclass
class LeadSubjectRelation(db.Model):
    """The main subjects done by the lead during a school year (represented here by lead_level_relation_id). Generally, we have 3 main subjects."""
    __tablename__ = 'lead_subject_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    lead_level_relation_id = db.Column(db.Integer, db.ForeignKey('lead_level_relation.id'), nullable=False)
    external_subject_id = db.Column(db.Integer, db.ForeignKey('external_subject.id'), nullable=False) # Soit external_subject_id soit subject_id, jamais les deux à la fois
    subject_id = db.Column(db.String(8), db.ForeignKey('subject.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=False) # 1, 2, 3
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
