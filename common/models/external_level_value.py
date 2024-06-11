
from dataclasses import dataclass
from . import db

# for lead process
@dataclass
class ExternalLevelValue(db.Model):
    """Intitulé de la série entrée par l'utilisateur lorsque celui n'existe pas dans l'object level_value"""
    __tablename__ = 'external_level_value'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=False)
    comments = db.Column(db.String(1024), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    
