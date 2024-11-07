from common.daos.countries_dao import countries_dao
from common.models.visa import Visa

class VisaService:
    def __init__(self, countries_dao):
        self.countries_dao = countries_dao

    @staticmethod
    def get_visatypes_by_country_iso2(country_iso2):
        print('##### get_visa_by_country_name ' + country_iso2)
        country_id = countries_dao.get_country_id_by_iso2(country_iso2)
        visatypes = Visa.query.filter_by(country_id=country_id).filter(Visa.id != 'vis00002').all()
        return [visatype.as_dict() for visatype in visatypes]
    
visa_service = VisaService(countries_dao)
