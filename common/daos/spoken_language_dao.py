from common.models.spoken_language import SpokenLanguage

class SpokenLanguageDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [spoken_language.as_dict() for spoken_language in self.model.query.all()]

spoken_language_dao = SpokenLanguageDAO(SpokenLanguage)
