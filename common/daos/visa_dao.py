from common.models.visa import Visa
class VisaDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [visa.as_dict() for visa in Visa.query.all()]
    
    def get_by_id(self, id):
        return Visa.query.get(id)
    
    #def get_by_country_name(self, country_name):
    #    return Visa.query.join(Visa.country_id).filter_by(name=country_name).all()

visa_dao = VisaDAO(Visa)
