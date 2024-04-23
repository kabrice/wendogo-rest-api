
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class Passport(db.Model):
    """Information sur le passeport de l'utilisateur"""
    __tablename__ = 'passport'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    delivery_place = db.Column(db.String(255), nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    passport_number = db.Column(db.String(255), nullable=False)
    comments = db.Column(db.String(1024), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
