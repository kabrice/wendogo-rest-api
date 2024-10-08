from common.models.mark_system import MarkSystem

class MarkSystemDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [mark_system.as_dict() for mark_system in MarkSystem.query.all()]
    
mark_system_dao = MarkSystemDAO(MarkSystem)
