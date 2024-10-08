from common.models.subject_weight_system import SubjectWeightSystem

class SubjectWeightSystemDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [subject_weight_system.as_dict() for subject_weight_system in SubjectWeightSystem.query.all()]
    
subject_weight_system_dao = SubjectWeightSystemDAO(SubjectWeightSystem)
