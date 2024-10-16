from common.models.level import Level

class LevelDAO:
    def __init__(self, model):
        self.model = model    
    
    """Recupérer les niveaux du lycée traités dans le simulateur"""
    def get_high_school_levels(self):
        return [level.as_dict() for level in Level.query.filter(Level.id.in_(['lev0002', 'lev0003'])).all()] 
    def get_degree_by_bac_id(self, bac_id):
        return [level.degree.as_dict() for level in Level.query.filter_by(bac_id=bac_id).filter(Level.degree_id != 'deg00004').all()]
    
level_dao = LevelDAO(Level)
