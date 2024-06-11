from common.models.user import User
#from models import db


class UserDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [user.as_dict() for user in User.query.all()]

user_dao = UserDAO(User)
