
from dataclasses import dataclass
from . import db

@dataclass
class Domain(db.Model):
    """Domaine d'etude (Informatique, Mathematiques, etc.) faisant le lien entre plusieurs sous-domaines."""
    __tablename__ = 'domain'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=False) # Niveau d'etude d'entrée pour le domaine (Licence, Master 1, Master 2,  Doctorat, etc.)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
