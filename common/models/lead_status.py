
from dataclasses import dataclass
from . import db

@dataclass
class LeadStatus(db.Model):

    __tablename__ = 'lead_status'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}    

    def as_dict_list(lead_status_list):
        return [lead_status.as_dict() for lead_status in lead_status_list]
        