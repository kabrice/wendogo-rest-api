from common.models.subject import Subject

class SubjectDAO:
    def __init__(self, model):
        self.model = model

    def _filter_subjects(self, **filters):
        """Utility method to apply filters and return subjects as dictionaries."""
        return [subject.as_dict() for subject in self.model.query.filter_by(**filters).all()]

    def get_all_subject_names(self):
        """Fetch all non-technical subject names."""
        return [subject.name for subject in self.model.query.filter_by(is_tech=False).all()]

    def get_subjects_by_level_id(self, applying_for_master):
        """Fetch subjects based on whether the level is university or not."""
        print(f'🥶 applying_for_master: {str(applying_for_master)}')
        filter_condition = self.model.level_id >= 'lev0013' if applying_for_master else self.model.level_id < 'lev0013'
        return [
            subject.as_dict() for subject in self.model.query
            .filter(filter_condition, self.model.is_tech.is_(False))
            .all()
        ]
    def get_all_subjects(self):
        """Fetch all subjects."""
        return [subject.as_dict() for subject in self.model.query.all()]

    def get_all(self):
        """Fetch all non-technical subjects."""
        return self._filter_subjects(is_tech=False)

# Initialize the subject DAO
subject_dao = SubjectDAO(Subject)
