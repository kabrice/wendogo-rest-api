from common.models.nationality import Nationality

class NationalityDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all_nationalities(self):
        return [nationality.as_dict() for nationality in self.model.query.all()]
        
nationality_dao = NationalityDAO(Nationality)
     