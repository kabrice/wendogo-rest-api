from common.models.lead_status import LeadStatus
#from models import db


class LeadStatusDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [lead_status.as_dict() for lead_status in LeadStatus.query.all()]
        #return LeadStatus.query.all()

lead_status_dao = LeadStatusDAO(LeadStatus)
