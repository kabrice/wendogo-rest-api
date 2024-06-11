from common.models.level import Level

class LevelDAO:
    def __init__(self, model):
        self.model = model    
    
    """Recupérer les niveaux du lycée traités dans le simulateur"""
    def get_high_school_levels(self):
        return [level.as_dict() for level in Level.query.filter(Level.id.in_(['lev0002', 'lev0003'])).all()] 
    
level_dao = LevelDAO(Level)
