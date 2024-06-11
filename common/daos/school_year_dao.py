from common.models.school_year import SchoolYear

class SchoolYearDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [school_year.as_dict() for school_year in SchoolYear.query.all()]
school_year_dao = SchoolYearDAO(SchoolYear)
