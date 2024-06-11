from common.models.countries import Countries
from common.models import db

class CountriesDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_country_id_by_iso2(self, iso2):
        try:
            print(f"1: {iso2}")
            country = Countries.query.filter_by(iso2=iso2).first()
            #print(f"country😍: {country}")
            if country:
                return country.id
            else:
                return None
        except Exception as e:
            # Handle any exceptions here
            print(f"An error occurred: {str(e)}")
            return None
        
    def get_all(self):
        return [country.as_dict() for country in Countries.query.all()]
        
countries_dao = CountriesDAO(Countries)
