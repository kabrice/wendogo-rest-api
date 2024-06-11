
from dataclasses import dataclass
from . import db

@dataclass
class Lead(db.Model):
    """Prospect qui sera plus tard converti en compte."""
    __tablename__ = 'lead'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    visa_id = db.Column(db.String(8), db.ForeignKey('visa.id'), nullable=True) # visa seeked by the user
    can_finance = db.Column(db.Boolean, nullable=True)
    french_level = db.Column(db.String(8), nullable=True) # Mauvais, Moyen, Bon, Tres bon, Excellent
    can_prove_french_level = db.Column(db.Boolean, nullable=True)
    english_level = db.Column(db.String(8), nullable=True) # Mauvais, Moyen, Bon, Tres bon, Excellent
    can_prove_english_level = db.Column(db.Boolean, nullable=True) 
    number_of_repeats_n_3 = db.Column(db.Integer, nullable=True)  # n is the last or current academic year. Here it's entered how many times the student has repeated the year during n-3.
    number_of_blank_years = db.Column(db.Integer, nullable=True) # n is the last or current academic year. Here it's entered how many years the student has been out of school during n-3.
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
