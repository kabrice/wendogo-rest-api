from common.daos.subject_dao import subject_dao
import unicodedata
from typing import List, Dict

class SubjectService:
    def __init__(self, subject_dao):
        self.subject_dao = subject_dao

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text by casefolding and removing accents."""
        normalized = unicodedata.normalize('NFKD', text.casefold())
        return ''.join(c for c in normalized if not unicodedata.combining(c))
    
    def string_to_bool(value):
        return value.lower() in ['true', '1', 'yes', 'y', 'on']

        # Usage
        print(string_to_bool("True"))  # Output: True
        print(string_to_bool("false")) # Output: False
        print(string_to_bool("1"))     # Output: True
        print(string_to_bool("0"))     # Output: False

    def get_search_subject_matches_from_user_input(self, is_university_level: str, external_subject_input: str) -> List[Dict]:
        # Fetch subjects based on level_id if provided, otherwise get all subjects
        #is_university_level = is_university_level.lower() in ['true', '1', 'yes', 'y', 'on']
        print(f'🥶 is_university_level: {is_university_level} and external_subject_input: {external_subject_input}')
        subjects =  self.subject_dao.get_subjects_by_level_id(is_university_level)
        
        normalized_input = self.normalize_text(external_subject_input)

        # Remove duplicates and normalize names in a single pass
        unique_subjects = {subject['name']: subject for subject in subjects}.values()

        # Find matches and limit results to 30
        matches = [
            subject for subject in unique_subjects
            if normalized_input in self.normalize_text(subject['name'])
        ][:30]

        return matches

# Initialize the subject service with the subject DAO
subject_service = SubjectService(subject_dao)
