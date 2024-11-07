
from dataclasses import dataclass
from . import db

@dataclass
class Level(db.Model):
    "level of study corresponding to the baccalaureate level (Bac+1, Bac+2, etc) and the degree level (DUT, BTS, License, Master, etc.)"
    __tablename__ = 'level'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True) # id is in the form of lev0001, lev0002, lev0003, etc
    degree_id = db.Column(db.String(8), db.ForeignKey('degree.id'), nullable=False) #  deg00004 =>French Baccalaureate, deg00005 => BTS, deg00006 => DUT … deg00008=>Licence, deg00009=>Master
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=False) # bac00001 => Bac-3, bac00002 => Bac-2, bac00003 => Bac-1, bac00004 => Bac+1, bac00005 => Bac+2, bac00006 => Bac+3, bac00007 => Bac+4, bac00008 => Bac+5
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    degree = db.relationship('Degree', backref=db.backref('levels', lazy=True))
    bac = db.relationship('Bac', backref=db.backref('levels', lazy=True))

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
