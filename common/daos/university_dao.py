from common.models.university import University 

class UniversityDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_universities_from_ids(self, university_ids):
        return [university.as_dict() for university in self.model.query.filter(self.model.id.in_(university_ids)).all()]
        
university_dao = UniversityDAO(University)
