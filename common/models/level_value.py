
from dataclasses import dataclass
from . import db

@dataclass
class LevelValue(db.Model):
    """Différents domaines d'études possible (Physique, Chimie, Action et communication commerciales, Biologie moléculaire, etc.) existant en base de données"""    

    __tablename__ = 'level_value'
    __table_args__ = {'extend_existing': True} 
    cache_ok = True

    id = db.Column(db.String(8), primary_key=True)
    code = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def as_dict(self):
        excluded_fields = ['code', 'created_at', 'updated_at','created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
