from common.models.bac import Bac

class BacDAO:
    def __init__(self, model):
        self.model = model    
    
    """Recupérer les bacs des universités traitées dans le simulateur"""
    def get_bacs_of_university(self):
        return [bac.as_dict() for bac in Bac.query.all() if bac.id not in ['bac00001', 'bac00002', 'bac00003']] 

bac_dao = BacDAO(Bac)
