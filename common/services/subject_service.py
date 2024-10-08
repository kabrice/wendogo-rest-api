from common.daos.subject_dao import subject_dao
from common.helper import Helper
import unicodedata


class SubjectService:
    def __init__(self, subject_dao):
        self.subject_dao = subject_dao 
    
    @staticmethod
    def get_search_subject_matches_from_user_input(external_subject_input):
        subjects = subject_dao.get_all()
        unique_subjects = {subject['name']: subject for subject in subjects}.values()
        matches = []
        count = 0
        for subject in unique_subjects:
            normalized_input = unicodedata.normalize('NFKD', external_subject_input.casefold())
            normalized_name = unicodedata.normalize('NFKD', subject['name'].casefold())
            normalized_input = ''.join(c for c in normalized_input if not unicodedata.combining(c))
            normalized_name = ''.join(c for c in normalized_name if not unicodedata.combining(c))
            if normalized_input in normalized_name:
                matches.append(subject)
                count += 1
            if count >= 30:
                break
        return matches
subject_service = SubjectService(subject_dao)
