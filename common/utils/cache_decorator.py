# common/utils/cache_decorator.py - VERSION MODIFIÉE avec support i18n

import functools
import json
import time
from datetime import datetime, timedelta, timezone
from flask import current_app, jsonify, request
import hashlib
from common.services.domain_service import DomainService
from common.models.program import Program
from common.models.subdomain import Subdomain
from common.utils.i18n_helpers import get_localized_field
from sqlalchemy import or_


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

@cached(timeout=3600, key_prefix='domains')
def get_cached_domains(locale='fr'):
    
    domains = DomainService.get_domains_with_active_programs_optimized(locale)
    
    localized_domains = []
    for domain in domains:
        # Si EN, recalculer le comptage pour programmes EN uniquement
        if locale == 'en':
            subdomain_ids = [sd['id'] for sd in domain.get('subdomains', [])]
            
            # Compter programmes EN
            total_en = Program.query.filter(
                Program.is_active == True,
                or_(
                    Program.sub_domain1_id.in_(subdomain_ids),
                    Program.sub_domain2_id.in_(subdomain_ids),
                    Program.sub_domain3_id.in_(subdomain_ids)
                ),
                Program.name_en.isnot(None),
                Program.name_en != ''
            ).distinct().count()
            
            # Recalculer pour chaque subdomain
            localized_subdomains = []
            for subdomain in domain.get('subdomains', []):
                count_en = Program.query.filter(
                    Program.is_active == True,
                    or_(
                        Program.sub_domain1_id == subdomain['id'],
                        Program.sub_domain2_id == subdomain['id'],
                        Program.sub_domain3_id == subdomain['id']
                    ),
                    Program.name_en.isnot(None),
                    Program.name_en != ''
                ).distinct().count()
                
                if count_en > 0:  # Ne garder que ceux avec programmes EN
                    localized_subdomains.append({
                        'id': subdomain['id'],
                        'domain_id': subdomain['domain_id'],
                        'name': subdomain.get('name_en') or subdomain['name'],
                        'program_count': count_en
                    })
            
            if total_en > 0:
                localized_domains.append({
                    'id': domain['id'],
                    'level_id': domain.get('level_id'),
                    'name': domain.get('name_en') or domain['name'],
                    'total_programs': total_en,
                    'subdomains': localized_subdomains
                })
        else:
            # FR : utiliser les comptages existants
            localized_domains.append({
                'id': domain['id'],
                'level_id': domain.get('level_id'),
                'name': domain['name'],
                'total_programs': domain.get('total_programs', 0),
                'subdomains': [
                    {
                        'id': sd['id'],
                        'domain_id': sd['domain_id'],
                        'name': sd['name'],
                        'program_count': sd['program_count']
                    }
                    for sd in domain.get('subdomains', [])
                ]
            })
    
    return localized_domains

@cached(timeout=1800, key_prefix='subdomains')  # Cache global de 30min
def get_cached_subdomains(locale='fr', domain_id=None):
    """
    Fonction interne cachée pour récupérer les subdomains
    Le cache est différencié par les arguments (locale, domain_id)
    """
    current_app.logger.info(f"🔍 get_cached_subdomains called with locale={locale}, domain_id={domain_id}")
    
    query = Subdomain.query
    
    if domain_id:
        query = query.filter_by(domain_id=domain_id)
    
    subdomains = query.all()
    
    result = []
    for subdomain in subdomains:
        # ✅ Localiser le nom selon la locale
        localized_name = get_localized_field(subdomain, 'name', locale)
        
        subdomain_dict = {
            'id': subdomain.id,
            'name': localized_name,  # ✅ Déjà localisé
            'domain_id': subdomain.domain_id,
            'program_count': subdomain.program_count if hasattr(subdomain, 'program_count') else 0
        }
        
        result.append(subdomain_dict)
    
    current_app.logger.info(f"✅ Cached {len(result)} subdomains for locale={locale}")
    if result:
        current_app.logger.debug(f"📝 First subdomain: {result[0]}")
    
    return result

# ✅ Cache pour les écoles (pas de localisation nécessaire)
@cached(timeout=1800, key_prefix='schools')  # 30 minutes
def get_cached_schools_preview():
    """Cache l'aperçu des écoles"""
    from common.daos.school_dao import school_dao
    return school_dao.get_schools_preview()

# ✅ Cache pour les options de filtres (pas de localisation)
@cached(timeout=900, key_prefix='filters')  # 15 minutes
def get_cached_filter_options():
    """Cache les options de filtres"""
    from common.daos.program_dao import program_dao
    return program_dao.get_filter_options()

# ✅ Cache pour les statistiques AVEC LOCALE
@cached(timeout=600, key_prefix='stats')
def get_cached_global_stats(locale='fr'):
    """
    Cache les statistiques globales
    En mode anglais, filtre uniquement les programmes avec traduction anglaise
    """
    from common.daos.program_dao import program_dao
    from common.daos.school_dao import school_dao
    from common.models.program import Program
    from common.models import db
    
    if locale == 'en':
        try:
            # Compter programmes EN
            program_count = Program.query.filter(
                Program.is_active == True,
                Program.name_en.isnot(None),
                Program.name_en != ''
            ).count()
            
            # Compter écoles distinctes avec programmes EN
            from sqlalchemy import func, distinct
            school_count = db.session.query(
                func.count(distinct(Program.school_id))
            ).filter(
                Program.is_active == True,
                Program.name_en.isnot(None),
                Program.name_en != '',
                Program.school_id.isnot(None)
            ).scalar()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            program_count = program_dao.get_programs_count()
            school_count = school_dao.get_schools_count()
    else:
        # FR : Tous les programmes actifs
        program_count = program_dao.get_programs_count()
        school_count = school_dao.get_schools_count()
    
    return {
        'total_programs': program_count,
        'total_schools': school_count,
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
    def clear_locale_cache(locale):
        """Vide le cache pour une locale spécifique"""
        CacheManager.clear_pattern(f":{locale}")
        current_app.logger.info(f"🗑️ Cleared cache for locale: {locale}")
    
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
            # Précharger les données principales pour FR et EN
            get_cached_domains('fr')
            get_cached_domains('en')
            get_cached_schools_preview()
            get_cached_filter_options()
            get_cached_global_stats('fr')
            get_cached_global_stats('en')
            
            current_app.logger.info("✅ Cache warm-up completed")
        except Exception as e:
            current_app.logger.error(f"❌ Cache warm-up failed: {e}")

# ✅ Headers de cache HTTP
def add_cache_headers(response, max_age=1800):
    """Ajoute les headers de cache HTTP"""
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    response.headers['ETag'] = f'"{hash(response.get_data())}"'
    response.headers['Last-Modified'] = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# ✅ Middleware de cache HTTP
def init_cache_middleware(app):
    @app.after_request
    def add_cache_headers_middleware(response):
        from flask import request
        
        # Ajouter des headers de cache pour les endpoints statiques
        static_endpoints = ['/domains', '/schools/preview', '/programs/filter-options', '/stats']
        
        if any(request.path.startswith(endpoint) for endpoint in static_endpoints):
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        
        return response
