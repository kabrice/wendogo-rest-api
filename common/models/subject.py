
from dataclasses import dataclass
from . import db

@dataclass
class Subject(db.Model):
    """Subject used in the application of courses."""
    __tablename__ = 'subject'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    code = db.Column(db.String(8), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.String(8), db.ForeignKey('subject.id'), nullable=True) # Parent subject
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=True) # Level related to the subject
    is_tech = db.Column(db.Boolean, default=False) # Technical subject used in the process and not shown to the user
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['code', 'created_at', 'parent_id', 'level_id', 'updated_at','created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
