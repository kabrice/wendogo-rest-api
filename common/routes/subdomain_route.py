# common/routes/subdomain_route.py
from flask import request, jsonify
from common.daos.subdomain_dao import subdomain_dao
from common.models.subdomain import Subdomain
from common.utils.i18n_helpers import get_localized_field, get_locale_from_request
from common.utils.cache_decorator import get_cached_subdomains, add_cache_headers

def init_routes(app):
    # @app.route('/subdomains', methods=['GET'])
    # def get_all_subdomains():
    #     """Récupère tous les sous-domaines avec leur domaine parent"""
    #     subdomains = subdomain_dao.get_all_subdomains()
    #     return jsonify(subdomains)
    
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
        locale = get_locale_from_request(request)
        subdomain_ids = request.json.get('subdomain_ids', [])
        if not subdomain_ids:
            return jsonify({"error": "subdomain_ids required"}), 400
        
        subdomains = subdomain_dao.get_subdomains_from_ids(subdomain_ids, locale)
        return jsonify(subdomains)
    
    @app.route('/subdomains/by-domain/<string:domain_id>', methods=['GET'])
    def get_subdomains_by_domain(domain_id):
        """Récupère tous les sous-domaines d'un domaine"""
        subdomains = subdomain_dao.get_subdomains_by_domain_id(domain_id)
        return jsonify(subdomains)

    @app.route('/subdomains', methods=['GET'])
    def get_subdomains():
        """Récupère les sous-domaines avec support i18n (AVEC CACHE)"""
        locale = get_locale_from_request(request)
        domain_id = request.args.get('domain_id')  # Garde comme string ou None
        
        app.logger.info(f"🌍 GET /subdomains - locale={locale}, domain_id={domain_id}")
        
        try:
            # ✅ Utiliser la version cachée avec locale
            subdomains = get_cached_subdomains(locale, domain_id)
            
            response = jsonify({
                'success': True,
                'data': subdomains
            })
            
            # Ajouter headers de cache HTTP
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        
        except Exception as e:
            app.logger.error(f"❌ Error in get_subdomains: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
