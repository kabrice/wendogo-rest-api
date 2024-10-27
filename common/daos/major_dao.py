from common.models.major import Major 

class MajorDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_major_subdomains_from_ids(self, major_ids): 
        majors = self.model.query.filter(self.model.id.in_(major_ids)).all()
        result = []
        for major in majors:
            subdomain = major.subdomain
            domain = subdomain.domain if subdomain else None
            result.append({
                'major_id': major.id, 
                'subdomain_id': subdomain.id,
                'subdomain_name': subdomain.name,
                'domain_id': domain.id if domain else None,
                'domain_name': domain.name if domain else None
            })
        return result
        
major_dao = MajorDAO(Major)
