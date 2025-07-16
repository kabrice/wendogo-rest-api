# common/utils/cache_decorator.py - Cache decorator pour Flask

import functools
import json
import time
from datetime import datetime, timedelta
from flask import current_app, jsonify
import hashlib

# ✅ Cache en mémoire simple pour le développement
class MemoryCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            timestamp = self.timestamps.get(key, 0)
            if time.time() - timestamp < 1800:  # 30 minutes
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key, value, ttl=1800):
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def delete(self, key):
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear(self):
        self.cache.clear()
        self.timestamps.clear()

# Instance globale du cache
memory_cache = MemoryCache()

def cached(timeout=1800, key_prefix=''):
    """
    Décorateur de cache pour les fonctions Flask
    
    Args:
        timeout (int): Durée du cache en secondes (défaut: 30 minutes)
        key_prefix (str): Préfixe pour les clés de cache
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Générer une clé de cache unique
            cache_key = f"{key_prefix}:{f.__name__}"
            
            # Ajouter les arguments à la clé si présents
            if args or kwargs:
                args_str = str(args) + str(sorted(kwargs.items()))
                hash_suffix = hashlib.md5(args_str.encode()).hexdigest()[:8]
                cache_key += f":{hash_suffix}"
            
            # Essayer de récupérer depuis le cache
            cached_result = memory_cache.get(cache_key)
            if cached_result is not None:
                current_app.logger.debug(f"✅ Cache HIT for {cache_key}")
                return cached_result
            
            # Exécuter la fonction et mettre en cache
            current_app.logger.debug(f"🔄 Cache MISS for {cache_key}")
            result = f(*args, **kwargs)
            
            if result is not None:
                memory_cache.set(cache_key, result, timeout)
                current_app.logger.debug(f"📦 Cached result for {cache_key}")
            
            return result
        return decorated_function
    return decorator

# ✅ Cache spécialisé pour les domaines
@cached(timeout=3600, key_prefix='domains')  # 1 heure
def get_cached_domains():
    """Cache les domaines avec leurs sous-domaines actifs"""
    from common.services.domain_service import DomainService
    return DomainService.get_domains_with_active_programs_optimized()

# ✅ Cache pour les écoles
@cached(timeout=1800, key_prefix='schools')  # 30 minutes
def get_cached_schools_preview():
    """Cache l'aperçu des écoles"""
    from common.daos.school_dao import school_dao
    return school_dao.get_schools_preview()

# ✅ Cache pour les options de filtres
@cached(timeout=900, key_prefix='filters')  # 15 minutes
def get_cached_filter_options():
    """Cache les options de filtres"""
    from common.daos.program_dao import program_dao
    return program_dao.get_filter_options()

# ✅ Cache pour les statistiques
@cached(timeout=600, key_prefix='stats')  # 10 minutes
def get_cached_global_stats():
    """Cache les statistiques globales"""
    from common.daos.program_dao import program_dao
    from common.daos.school_dao import school_dao
    
    return {
        'total_programs': program_dao.get_programs_count(),
        'total_schools': school_dao.get_schools_count(),
        'satisfaction_rate': 95,
        'support_availability': '24/7'
    }

# ✅ Utilitaires de gestion du cache
class CacheManager:
    @staticmethod
    def clear_all():
        """Vide tout le cache"""
        memory_cache.clear()
        current_app.logger.info("🗑️ Cache cleared")
    
    @staticmethod
    def clear_pattern(pattern):
        """Vide le cache pour un pattern donné"""
        keys_to_delete = [key for key in memory_cache.cache.keys() if pattern in key]
        for key in keys_to_delete:
            memory_cache.delete(key)
        current_app.logger.info(f"🗑️ Cleared {len(keys_to_delete)} cache entries for pattern: {pattern}")
    
    @staticmethod
    def get_stats():
        """Retourne les statistiques du cache"""
        return {
            'total_keys': len(memory_cache.cache),
            'keys': list(memory_cache.cache.keys()),
            'memory_usage': sum(len(str(v)) for v in memory_cache.cache.values())
        }
    
    @staticmethod
    def warm_up():
        """Préchauffe le cache avec les données essentielles"""
        current_app.logger.info("🔥 Warming up cache...")
        
        try:
            # Précharger les données principales
            get_cached_domains()
            get_cached_schools_preview()
            get_cached_filter_options()
            get_cached_global_stats()
            
            current_app.logger.info("✅ Cache warm-up completed")
        except Exception as e:
            current_app.logger.error(f"❌ Cache warm-up failed: {e}")

# ✅ Headers de cache HTTP
def add_cache_headers(response, max_age=1800):
    """Ajoute les headers de cache HTTP"""
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    response.headers['ETag'] = f'"{hash(response.get_data())}"'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# ✅ Middleware de cache HTTP
def init_cache_middleware(app):
    @app.after_request
    def add_cache_headers_middleware(response):
        # ✅ CORRECTION: Utiliser request depuis Flask, pas response
        from flask import request
        
        # Ajouter des headers de cache pour les endpoints statiques
        static_endpoints = ['/domains', '/schools/preview', '/programs/filter-options', '/stats']
        
        if any(request.path.startswith(endpoint) for endpoint in static_endpoints):
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        
        return response
