
from dataclasses import dataclass
from . import db

@dataclass
class Cities(db.Model):

    __tablename__ = 'cities'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
