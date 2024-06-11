
from dataclasses import dataclass
from . import db

@dataclass
class Level(db.Model):
    "Niveau éducatif (2nd, 1ère, Terminale, Bac, L1, L2, Licence, Master 1, Master 2, Doctorat, Bts, Dut, CPGE etc.)"
    __tablename__ = 'level'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    degree_id = db.Column(db.String(8), db.ForeignKey('degree.id'), nullable=False)
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
