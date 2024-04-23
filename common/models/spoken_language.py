
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class SpokenLanguage(db.Model):
    """Français, Anglais, etc."""
    __tablename__ = 'spoken_language'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.value: getattr(self, c.value) for c in self.__table__.columns if c.name not in excluded_fields}    
