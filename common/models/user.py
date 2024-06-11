from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.event import listens_for
from . import db

@dataclass
class User(db.Model):

    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(255), nullable=True)
    street = db.Column(db.String(255), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True) 
    city = db.Column(db.String(35), nullable=True)#2
    description = db.Column(db.String(2500), nullable=True)#2
    email = db.Column(db.String(50), nullable=True)#1
    firstname = db.Column(db.String(46), nullable=True)#1
    lastname = db.Column(db.String(46), nullable=True)#1
    birthdate = db.Column(db.Date)#1
    salutation = db.Column(db.String(15), nullable=True)#1
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    country = db.Column(db.String(4), nullable=True)
    updated_at = db.Column(db.DateTime)
    phone = db.Column(db.String(25), nullable=True)
    has_whatsapp = db.Column(db.Boolean, unique=False, default=False, nullable=True)
    whatsapp_verification_attempt = db.Column(db.Integer, default=0)
    occupation = db.Column(db.String(20), nullable=True)#2
    subscription_step = db.Column(db.String(255), nullable=True) # next page where user should be redirected
    nationality_id = db.Column(db.String(8), db.ForeignKey('nationality.id'), nullable=True)
    passport_id = db.Column(db.Integer, db.ForeignKey('passport.id'), nullable=True)
    is_disabled = db.Column(db.Boolean, unique=False, default=False, nullable=True) # handicapé
    lead_status_id = db.Column(db.String(8), db.ForeignKey('lead_status.id'), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Parent user (Parent user can fill the form for his child)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, firstname='', lastname='', salutation='', city='', email='', phone='', occupation='', description='', country=''):
        self.firstname = firstname
        self.lastname = lastname
        self.salutation = salutation
        self.city = city
        self.email = email
        self.phone = phone
        self.occupation = occupation
        self.description = description
        self.country = country

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'whatsapp_verification_attempt']
        return {field.name:getattr(self, field.name) for field in self.__table__.c if field.name not in excluded_fields}
            
@listens_for(User, 'after_update')
def update_user_log(mapper, connection, target):
    user_table = User.__table__
    connection.execute(
        user_table.update().
        where(user_table.c.id==target.id).
        values(updated_at=datetime.utcnow())
    )
