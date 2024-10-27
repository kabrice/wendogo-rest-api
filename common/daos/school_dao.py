from common.models.school import School 

class SchoolDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_schools_from_ids(self, school_ids):
        schools = self.model.query.filter(self.model.id.in_(school_ids)).all()
        return [
            {
                **school.as_dict(),
                'university': school.university.as_dict() if school.university else None
            }
            for school in schools
        ]
        
school_dao = SchoolDAO(School)
