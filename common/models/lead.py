
from dataclasses import dataclass
from . import db
from sqlalchemy import event
from sqlalchemy.sql import func

@dataclass
class Lead(db.Model):
    """Prospect qui sera plus tard converti en compte."""
    __tablename__ = 'lead'
    __table_args__ = {'extend_existing': True} 
   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    visa_id = db.Column(db.String(8), db.ForeignKey('visa.id'), nullable=True) # visa seeked by the user
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=True) # bac of the user
    degree_id = db.Column(db.String(8), db.ForeignKey('degree.id'), nullable=True)
    can_finance = db.Column(db.Boolean, nullable=True)
    french_level = db.Column(db.String(8), nullable=True) # C2, C1, B2, B1, A2, A1
    can_prove_french_level = db.Column(db.Boolean, nullable=True)
    english_level = db.Column(db.String(8), nullable=True) # C2, C1, B2, B1, A2, A1
    can_prove_english_level = db.Column(db.Boolean, nullable=True) 
    number_of_repeats_n_3 = db.Column(db.Integer, nullable=True)  # n is the last or current academic year. Here it's entered how many times the student has repeated the year during n-3.
    number_of_blank_years = db.Column(db.Integer, nullable=True) # n is the last or current academic year. Here it's entered how many years the student has been out of school during n-3.
    other_spoken_language_id = db.Column(db.String(8), db.ForeignKey('spoken_language.id'), nullable=True)
    other_spoken_language_level = db.Column(db.String(8), nullable=True)
    can_prove_spoken_language_level = db.Column(db.Boolean, nullable=True) 
    french_travel_start_date = db.Column(db.Date, nullable=True)
    french_travel_end_date = db.Column(db.Date, nullable=True)
    evaluation_score = db.Column(db.Float, nullable=True)
    contacted_clicks = db.Column(db.Integer, default=0)
    project_message = db.Column(db.String(36000), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}   
     
# Add an event listener for updates
@event.listens_for(Lead, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = func.current_timestamp()
