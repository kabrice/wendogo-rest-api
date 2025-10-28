# common/routes/school_route.py - Version optimisée avec cache

from flask import request, jsonify
from common.daos.school_dao import school_dao
from common.utils.i18n_helpers import get_locale_from_request
from common.utils.cache_decorator import get_cached_schools_preview, add_cache_headers
from common.serializers import SchoolSerializer

def init_routes(app):
    @app.route('/schools/filtring', methods=['POST'])
    def get_school_details_from_school_ids():
        """Méthode existante - Récupère plusieurs écoles par leurs IDs"""
        school_ids = request.json.get('school_ids') #['sch0095', 'sch0140', etc]
        school_details = school_dao.get_schools_from_ids(school_ids)
        return jsonify(school_details)
    
    @app.route('/schools', methods=['GET'])
    def get_all_schools():
        """Récupère toutes les écoles publiques"""
        schools = school_dao.get_all_schools()
        response = jsonify(schools)
        return add_cache_headers(response, max_age=1800)  # 30 minutes
    
    @app.route('/schools/preview', methods=['GET'])
    def get_schools_preview():
        """Récupère un aperçu des écoles (AVEC CACHE)"""
        try:
            # Utiliser la version cachée
            schools = get_cached_schools_preview()
            response = jsonify(schools)
            
            # Ajouter headers de cache HTTP
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        except Exception as e:
            print(f"❌ Error in get_schools_preview: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/schools/<string:school_id>', methods=['GET'])
    def get_school_by_id(school_id):
        """Récupère une école par son ID"""
        school = school_dao.get_school_by_id(school_id)
        locale = get_locale_from_request(request)
        if school:
            serialized = SchoolSerializer.serialize(
                school,
                locale=locale
            )
            response = jsonify(serialized)
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        return jsonify({"error": "School not found"}), 404
    
    @app.route('/schools/slug/<string:slug>', methods=['GET'])
    def get_school_by_slug(slug):
        """Récupère une école par son slug"""
        school = school_dao.get_school_by_slug(slug)
        locale = get_locale_from_request(request)
        if school:
            serialized = SchoolSerializer.serialize(
                school,
                locale=locale
            )
            response = jsonify(serialized)
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        return jsonify({"error": "School not found"}), 404
    
    @app.route('/schools/slugs', methods=['GET'])
    def get_all_school_slugs():
        """Récupère tous les slugs des écoles (pour génération statique)"""
        slugs = school_dao.get_all_school_slugs()
        response = jsonify(slugs)
        return add_cache_headers(response, max_age=3600)  # 1 heure
    
    @app.route('/schools/search', methods=['POST'])
    def search_schools():
        """Recherche d'écoles avec filtres"""
        filters = request.json or {}
        schools = school_dao.search_schools(filters)
        return jsonify(schools)
    
    @app.route('/schools/<string:school_id>/similar', methods=['GET'])
    def get_similar_schools(school_id):
        """Récupère les écoles similaires"""
        limit = request.args.get('limit', 3, type=int)
        similar_schools = school_dao.get_similar_schools(school_id, limit)
        response = jsonify(similar_schools)
        return add_cache_headers(response, max_age=1800)  # 30 minutes
    
    @app.route('/schools/stats', methods=['GET'])
    def get_schools_stats():
        """Récupère les statistiques des écoles"""
        total_schools = school_dao.get_schools_count()
        response = jsonify({
            'total_schools': total_schools
        })
        return add_cache_headers(response, max_age=900)  # 15 minutes
