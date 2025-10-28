# common/daos/subdomain_dao.py
from common.models.subdomain import Subdomain

class SubdomainDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all_subdomains(self):
        """Récupère tous les sous-domaines avec leur domaine parent"""
        subdomains = self.model.query.all()
        result = []
        for subdomain in subdomains:
            subdomain_data = subdomain.as_dict()
            # Ajouter les infos du domaine parent
            if subdomain.domain:
                subdomain_data['domain_name'] = subdomain.domain.name
                subdomain_data['domain_level_id'] = subdomain.domain.level_id
            result.append(subdomain_data)
        return result
    
    def get_subdomain_by_id(self, subdomain_id):
        """Récupère un sous-domaine par son ID"""
        subdomain = self.model.query.filter_by(id=subdomain_id).first()
        if subdomain:
            subdomain_data = subdomain.as_dict()
            if subdomain.domain:
                subdomain_data['domain_name'] = subdomain.domain.name
                subdomain_data['domain_level_id'] = subdomain.domain.level_id
            return subdomain_data
        return None
    
    def get_subdomains_from_ids(self, subdomain_ids, locale='fr'):
        """Récupère plusieurs sous-domaines par leurs IDs"""
        subdomains = self.model.query.filter(self.model.id.in_(subdomain_ids)).all()
        result = []
        for subdomain in subdomains:
            subdomain_data = subdomain.as_dict()
            if subdomain.domain:
                subdomain_data['domain_name'] = subdomain.domain.name if locale == 'fr' else subdomain.domain.name_en
                subdomain_data['name'] = subdomain.name if locale == 'fr' else subdomain.name_en
                subdomain_data['domain_level_id'] = subdomain.domain.level_id
            result.append(subdomain_data)
        return result
    
    def get_subdomains_by_domain_id(self, domain_id):
        """Récupère tous les sous-domaines d'un domaine"""
        subdomains = self.model.query.filter_by(domain_id=domain_id).all()
        return [subdomain.as_dict() for subdomain in subdomains]

subdomain_dao = SubdomainDAO(Subdomain)
