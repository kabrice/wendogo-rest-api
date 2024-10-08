
from dataclasses import dataclass
from . import db
@dataclass
class CourseLevelRelation(db.Model):
    "Different level values that a course can have."

    __tablename__ = 'course_level_relation'
    __table_args__ = {'extend_existing': True} 

    id = db.Column(db.String(8), primary_key=True) # course_level_relation id is the form of clv0001, clv0002, etc.
    course_id = db.Column(db.String(8), db.ForeignKey('course.id'), nullable=False)
    bac_id = db.Column(db.String(8), db.ForeignKey('bac.id'), nullable=False) # Minimum bac level required to access the course (bac00004 =>  bac+1 , bac00005=> bac+2, bac00006=>bac+3, etc)
    level_value_id = db.Column(db.String(8), db.ForeignKey('level_value.id'), nullable=False)
    minimum_score = db.Column(db.Float, nullable=False) # Minimum general average mark of the most recent to access the course (For example: 12/20, etc.)
    priority = db.Column(db.Integer, nullable=False) # order of importance for the course (exemple : C>D>A pour Tle)
    is_L1 = db.Column(db.Boolean, nullable=True, default=False) # True => Minimum general average mark is applicable for L1 (Licence 1)
    is_L2 = db.Column(db.Boolean, nullable=True, default=False) # True => Minimum general average mark is applicable for L2 (Licence 2)
    is_L3 = db.Column(db.Boolean, nullable=True, default=False) # True => Minimum general average mark is applicable for L3 (Licence 3)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    level_value = db.relationship('LevelValue', backref='course_level_relation') 
    course = db.relationship('Course', backref='course_level_relation')
    bac = db.relationship('Bac', backref='course_level_relation')

    def as_dict(self):
        excluded_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in excluded_fields}
