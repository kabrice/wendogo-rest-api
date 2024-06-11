
from dataclasses import dataclass
from . import db

@dataclass
class University(db.Model):
    "Université pouvant comporter plusieurs facultés et écoles (school)."
    
    __tablename__ = 'university'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True)
    external_id = db.Column(db.Integer, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    logo_path = db.Column(db.String(255), nullable=False)
    ranking = db.Column(db.Integer, nullable=False) # ranking in term of selectivity
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def as_dict(self):
        excluded_fields = ['id', 'created_at', 'updated_at']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
