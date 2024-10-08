from common.models.cities import Cities 
from common.models.countries import Countries

class CitiesDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_cities_by_country_iso2(self, iso2):
        return [city.as_dict() for city in self.model.query.join(Countries).filter(Countries.iso2 == iso2).all()]
         
    def get_all(self):
        return [city.as_dict() for city in Cities.query.all()]
        
cities_dao = CitiesDAO(Cities)
