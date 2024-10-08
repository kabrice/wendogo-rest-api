from common.daos.level_value_dao import level_value_dao
from common.helper import Helper
import unicodedata


class LevelValueService:
    def __init__(self, level_value_dao):
        self.level_value_dao = level_value_dao

    @staticmethod
    def get_best_level_value_match_from_user_input(external_level_value_input):
        level_values = level_value_dao.get_all()
        
        best_match = None
        best_similarity = 0
        id = None
        for level_value in level_values:
            if level_value:
                similarity = Helper.cosine_sim(external_level_value_input, level_value.get('name'))
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = level_value

        return best_match, best_similarity
    

    @staticmethod
    def get_search_level_value_matches_from_user_input(external_level_value_input):
        level_values = level_value_dao.get_all()
        matches = []
        count = 0
        for level_value in level_values:
            normalized_input = unicodedata.normalize('NFKD', external_level_value_input.casefold())
            normalized_name = unicodedata.normalize('NFKD', level_value['name'].casefold())
            normalized_input = ''.join(c for c in normalized_input if not unicodedata.combining(c))
            normalized_name = ''.join(c for c in normalized_name if not unicodedata.combining(c))
            if normalized_input in normalized_name:
                matches.append(level_value)
                count += 1
            if count >= 30:
                break
        return matches
level_value_service = LevelValueService(level_value_dao)
