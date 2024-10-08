
from dataclasses import dataclass
from . import db

@dataclass
class Cities(db.Model):

    __tablename__ = 'cities'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)

    def as_dict(self): 
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
