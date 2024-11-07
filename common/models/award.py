
from dataclasses import dataclass
from . import db
"""Recompenses en relation avec les 3 matières choisies par l'utilisateur au début de la simulation"""

@dataclass
class Award(db.Model):
    __tablename__ = 'award'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(255), nullable=False)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False) 
    spoken_language_id = db.Column(db.String(8), db.ForeignKey('spoken_language.id'), nullable=False) 
    honour_type = db.Column(db.String(15), nullable=True)
    rank = db.Column(db.Integer, nullable=True) 
    school_year_id = db.Column(db.String(8), db.ForeignKey('school_year.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
