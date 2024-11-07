from dataclasses import dataclass
from . import db

@dataclass
class Log(db.Model):

    __tablename__ = 'log'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(255), nullable=True)
    request_input = db.Column(db.String(255))
    message = db.Column(db.String(2500), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, default=1) 

    def __init__(self, request_input, message):
        self.request_input = request_input
        self.message = message
