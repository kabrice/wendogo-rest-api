
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class LeadLevelValueRelation(db.Model):
    """level value suggéré et selectionné par l'utilisateur au début de la simulation"""
    __tablename__ = 'lead_level_value_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False) 
    level_value_id = db.Column(db.String(8), db.ForeignKey('level_value.id'), nullable=False)
    external_degree_id = db.Column(db.Integer, db.ForeignKey('external_degree.id'), nullable=False)
    school_year_id = db.Column(db.String(8), db.ForeignKey('school_year.id'), nullable=False) # l'année d'étude la plus récente
    is_current_year = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Add relationship to external_degree for easy access to external_degree.name
    external_degree = db.relationship('ExternalDegree', backref='lead_level_value_relation')
    level_value = db.relationship('LevelValue', backref='lead_level_value_relation')
    school_year = db.relationship('SchoolYear', backref='lead_level_value_relation')
    
    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
