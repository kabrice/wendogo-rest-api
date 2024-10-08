from common.models.subject import Subject

class SubjectDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all_subject_name(self):
        return [subject.name for subject in self.model.query.all()]
    
    def get_all(self):
        return [subject.as_dict() for subject in self.model.query.all()]
    
subject_dao = SubjectDAO(Subject)

