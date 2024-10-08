from common.models.academic_year_organization import AcademicYearOrganization

class AcademicYearOrganizationDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all(self):
        return [academic_year_organization.as_dict() for academic_year_organization in AcademicYearOrganization.query.all()]
    
academic_year_organization_dao = AcademicYearOrganizationDAO(AcademicYearOrganization)
