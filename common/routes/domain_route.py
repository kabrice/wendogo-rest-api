# common/routes/domain_route.py - Version mise à jour

from flask import request, jsonify
from common.daos.domain_dao import domain_dao
from common.utils.cache_decorator import get_cached_domains, add_cache_headers

def init_routes(app):
    @app.route('/domains', methods=['GET'])
    def get_all_domains():
        """Récupère tous les domaines avec leurs sous-domaines qui ont des programmes"""
        # Utiliser la nouvelle méthode qui filtre par programmes
        domains = domain_dao.get_all_domains_with_programs()
        return jsonify(domains)
    
    @app.route('/domains/all', methods=['GET'])
    def get_all_domains_complete():
        """Récupère tous les domaines avec TOUS leurs sous-domaines (pour admin)"""
        # Garder l'ancienne méthode pour l'administration
        domains = domain_dao.get_all_domains()
        return jsonify(domains)
    
    @app.route('/domains/<string:domain_id>', methods=['GET'])
    def get_domain_by_id(domain_id):
        """Récupère un domaine par son ID avec sous-domaines actifs"""
        domain = domain_dao.get_domain_by_id(domain_id)
        if domain:
            return jsonify(domain)
        return jsonify({"error": "Domain not found"}), 404
    
    @app.route('/domains/filtering', methods=['POST'])
    def get_domains_from_ids():
        """Récupère plusieurs domaines par leurs IDs avec programmes"""
        domain_ids = request.json.get('domain_ids', [])
        if not domain_ids:
            return jsonify({"error": "domain_ids required"}), 400
        
        domains = domain_dao.get_domains_from_ids(domain_ids)
        return jsonify(domains)
    
    @app.route('/domains/<string:domain_id>/stats', methods=['GET'])
    def get_domain_stats(domain_id):
        """Récupère les statistiques d'un domaine"""
        from common.services.domain_service import DomainService
        
        total_programs = DomainService.get_domain_program_count(domain_id)
        return jsonify({
            'domain_id': domain_id,
            'total_programs': total_programs
        })
