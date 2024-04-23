
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class LeadLevelRelation(db.Model):
    """paramétrage et infos sur la série renseignée par l'utisateur. Permet d'avoir des infos académique sur une année donnée"""
    __tablename__ = 'lead_level_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=False)
    level_id = db.Column(db.String(8), db.ForeignKey('level.id'), nullable=False) # soit level_id soit external_level_value_id, jamais les deux à la fois
    external_level_value_id = db.Column(db.Integer, db.ForeignKey('external_level_value.id'), nullable=False)
    school_year_id = db.Column(db.String(8), db.ForeignKey('school_year.id'), nullable=False)
    is_current_year = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
