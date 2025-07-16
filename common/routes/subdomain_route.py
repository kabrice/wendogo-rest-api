# common/routes/subdomain_route.py
from flask import request, jsonify
from common.daos.subdomain_dao import subdomain_dao

def init_routes(app):
    @app.route('/subdomains', methods=['GET'])
    def get_all_subdomains():
        """Récupère tous les sous-domaines avec leur domaine parent"""
        subdomains = subdomain_dao.get_all_subdomains()
        return jsonify(subdomains)
    
    @app.route('/subdomains/<string:subdomain_id>', methods=['GET'])
    def get_subdomain_by_id(subdomain_id):
        """Récupère un sous-domaine par son ID"""
        subdomain = subdomain_dao.get_subdomain_by_id(subdomain_id)
        if subdomain:
            return jsonify(subdomain)
        return jsonify({"error": "Subdomain not found"}), 404
    
    @app.route('/subdomains/filtering', methods=['POST'])
    def get_subdomains_from_ids():
        """Récupère plusieurs sous-domaines par leurs IDs"""
        subdomain_ids = request.json.get('subdomain_ids', [])
        if not subdomain_ids:
            return jsonify({"error": "subdomain_ids required"}), 400
        
        subdomains = subdomain_dao.get_subdomains_from_ids(subdomain_ids)
        return jsonify(subdomains)
    
    @app.route('/subdomains/by-domain/<string:domain_id>', methods=['GET'])
    def get_subdomains_by_domain(domain_id):
        """Récupère tous les sous-domaines d'un domaine"""
        subdomains = subdomain_dao.get_subdomains_by_domain_id(domain_id)
        return jsonify(subdomains)
