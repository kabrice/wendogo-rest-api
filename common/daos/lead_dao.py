from common.models.lead import Lead
#from models import db


class LeadDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [user.as_dict() for user in Lead.query.all()]
    
    def get_by_id(self, id):
        return Lead.query.get(id)

lead_dao = LeadDAO(Lead)
