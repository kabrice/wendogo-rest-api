from common.models.degree import Degree
from common.models import db

class DegreeDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_degree_id_by_name(self, name):
        try:
            print(f"1: {name}")
            degree = Degree.query.filter_by(name=name).first()
            if degree:
                return degree.id
            else:
                return None
        except Exception as e:
            # Handle any exceptions here
            print(f"An error occurred: {str(e)}")
            return None
        
    def get_all(self):
        return [degree.as_dict() for degree in Degree.query.all()]
    
    def get_degree_by_id_list(self, id_list):
        return [degree.as_dict() for degree in Degree.query.filter(Degree.id.in_(id_list)).all()]
    
    def get_degree_by_not_in_id_list(self, id_list):
        return [degree.as_dict() for degree in Degree.query.filter(Degree.id.notin_(id_list)).all()]
    
degree_dao = DegreeDAO(Degree)
