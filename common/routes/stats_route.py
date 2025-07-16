# common/routes/stats_route.py - Version optimisée avec cache

from flask import jsonify
from common.utils.cache_decorator import get_cached_global_stats, add_cache_headers

def init_routes(app):
    @app.route('/stats', methods=['GET'])
    def get_global_stats():
        """Récupère toutes les statistiques globales (AVEC CACHE)"""
        try:
            # Utiliser la version cachée
            stats = get_cached_global_stats()
            response = jsonify(stats)
            
            # Ajouter headers de cache HTTP
            return add_cache_headers(response, max_age=600)  # 10 minutes
        except Exception as e:
            print(f"❌ Error in get_global_stats: {e}")
            return jsonify({"error": "Internal server error"}), 500
