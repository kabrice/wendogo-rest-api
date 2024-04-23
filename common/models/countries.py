
from dataclasses import dataclass
from . import db

@dataclass
class Countries(db.Model):

    __tablename__ = 'countries'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    
