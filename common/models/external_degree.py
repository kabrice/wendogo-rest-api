
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class ExternalDegree(db.Model):
    """Name of the diploma entered manually by the user (not yet existing in the database)"""
    __tablename__ = 'external_degree'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False) # ex: "Baccalauréat en sciences, option mathématiques et physique; Licence en droit privé; Master en sciences de l'ingénieur civil, orientation électricité"
    comments = db.Column(db.String(1024), nullable=True) 
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
