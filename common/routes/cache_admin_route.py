# common/routes/cache_admin_route.py - Routes admin pour la gestion du cache

from flask import jsonify, request
from common.utils.cache_decorator import CacheManager
from common.services.domain_service import DomainService

def init_routes(app):
    @app.route('/admin/cache/stats', methods=['GET'])
    def cache_stats():
        """Statistiques du cache"""
        try:
            stats = CacheManager.get_stats()
            
            # Ajouter infos sur les tables de cache DB
            cache_tables_exist = DomainService._cache_tables_exist()
            
            return jsonify({
                'success': True,
                'memory_cache': stats,
                'database_cache': {
                    'tables_exist': cache_tables_exist,
                    'status': 'active' if cache_tables_exist else 'not_configured'
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/admin/cache/clear', methods=['POST'])
    def clear_cache():
        """Vider le cache mémoire"""
        try:
            pattern = request.json.get('pattern') if request.json else None
            
            if pattern:
                CacheManager.clear_pattern(pattern)
                message = f"Memory cache cleared for pattern: {pattern}"
            else:
                CacheManager.clear_all()
                message = "All memory cache cleared successfully"
            
            return jsonify({
                'success': True,
                'message': message
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/admin/cache/warmup', methods=['POST'])
    def warmup_cache():
        """Préchauffer le cache mémoire"""
        try:
            CacheManager.warm_up()
            return jsonify({
                'success': True,
                'message': "Memory cache warmed up successfully"
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/admin/cache/refresh-db', methods=['POST'])
    def refresh_database_cache():
        """Rafraîchir les tables de cache DB"""
        try:
            success = DomainService.refresh_cache_tables()
            
            if success:
                return jsonify({
                    'success': True,
                    'message': "Database cache tables refreshed successfully"
                })
            else:
                return jsonify({
                    'success': False,
                    'error': "Cache tables not available or refresh failed"
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
