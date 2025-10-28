
from dataclasses import dataclass
from . import db

@dataclass
class Subdomain(db.Model):

    __tablename__ = 'subdomain'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    name_en = db.Column(db.String(255), nullable=True)
    domain_id = db.Column(db.String(8), db.ForeignKey('domain.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    domain = db.relationship('Domain', backref='subdomains')
        # Relations
    #programs = db.relationship('Program', backref='subdomain', lazy=True)

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
