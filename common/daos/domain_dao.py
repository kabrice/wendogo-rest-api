# common/daos/domain_dao.py - Version mise à jour

from common.models.domain import Domain
from common.models.subdomain import Subdomain
from common.services.domain_service import DomainService

class DomainDAO:
    def __init__(self, model):
        self.model = model    
    
    def get_all_domains(self):
        """Récupère tous les domaines avec leurs sous-domaines (ancienne version)"""
        domains = self.model.query.all()
        result = []
        for domain in domains:
            domain_data = domain.as_dict()
            # Ajouter les sous-domaines
            subdomains = []
            for subdomain in domain.subdomains:
                subdomains.append(subdomain.as_dict())
            domain_data['subdomains'] = subdomains
            result.append(domain_data)
        return result
    
    def get_all_domains_with_programs(self):
        """Récupère tous les domaines avec seulement les sous-domaines qui ont des programmes"""
        return DomainService.get_domains_with_active_programs_optimized()
    
    def get_domain_by_id(self, domain_id):
        """Récupère un domaine par son ID avec ses sous-domaines actifs"""
        domain = self.model.query.filter_by(id=domain_id).first()
        if domain:
            domain_data = domain.as_dict()
            
            # Ajouter seulement les sous-domaines qui ont des programmes
            active_subdomains = []
            for subdomain in domain.subdomains:
                program_count = DomainService.get_subdomain_program_count(subdomain.id)
                if program_count > 0:
                    subdomain_data = subdomain.as_dict()
                    subdomain_data['program_count'] = program_count
                    active_subdomains.append(subdomain_data)
            
            domain_data['subdomains'] = active_subdomains
            domain_data['total_programs'] = DomainService.get_domain_program_count(domain_id)
            return domain_data
        return None
    
    def get_domains_from_ids(self, domain_ids):
        """Récupère plusieurs domaines par leurs IDs avec programmes"""
        domains = self.model.query.filter(self.model.id.in_(domain_ids)).all()
        result = []
        for domain in domains:
            domain_data = domain.as_dict()
            
            # Ajouter seulement les sous-domaines qui ont des programmes
            active_subdomains = []
            for subdomain in domain.subdomains:
                program_count = DomainService.get_subdomain_program_count(subdomain.id)
                if program_count > 0:
                    subdomain_data = subdomain.as_dict()
                    subdomain_data['program_count'] = program_count
                    active_subdomains.append(subdomain_data)
            
            if active_subdomains:  # Ajouter seulement si il y a des sous-domaines actifs
                domain_data['subdomains'] = active_subdomains
                domain_data['total_programs'] = sum(sub['program_count'] for sub in active_subdomains)
                result.append(domain_data)
        
        return result
   
domain_dao = DomainDAO(Domain)
