
from dataclasses import dataclass
from . import db

@dataclass
class VisaCriteria(db.Model):
    """Criteria for visa evaluation."""
    __tablename__ = 'visa_criteria'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    score = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(1024), nullable=True)
    criteria_type_id = db.Column(db.String(8), db.ForeignKey('criteria_type.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
