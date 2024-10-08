from common.models.level_value import LevelValue

class LevelValueDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all_level_value_name(self):
        return [level_value.name for level_value in self.model.query.all()]
    
    def get_all(self):
        return [level_value.as_dict() for level_value in self.model.query.all()]
    
level_value_dao = LevelValueDAO(LevelValue)

