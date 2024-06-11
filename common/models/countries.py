
from dataclasses import dataclass
from . import db

@dataclass
class Countries(db.Model):

    __tablename__ = 'countries'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    iso2 = db.Column(db.String(2), nullable=False)
    
    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
