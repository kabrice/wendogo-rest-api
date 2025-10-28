# common/routes/stats_route.py - VERSION CORRIGÉE AVEC CACHE + i18n
from flask import jsonify, request
from common.utils.cache_decorator import get_cached_global_stats, add_cache_headers
from common.utils.i18n_helpers import get_locale_from_request

def init_routes(app):
    
    @app.route('/stats', methods=['GET'])
    def get_global_stats():
        """Récupère toutes les statistiques globales (AVEC CACHE + i18n)"""
        locale = get_locale_from_request(request)
        
        try:
            # Utiliser la version cachée avec locale
            stats = get_cached_global_stats(locale)
            response = jsonify({
                'success': True,
                'data': stats
            })
            
            # Ajouter headers de cache HTTP
            return add_cache_headers(response, max_age=600)  # 10 minutes
        
        except Exception as e:
            app.logger.error(f"❌ Error in get_global_stats: {e}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
