# common/routes/program_route.py - Version optimisée avec cache

from flask import request, jsonify
from common.daos.program_dao import program_dao
from common.utils.cache_decorator import get_cached_filter_options, add_cache_headers
from pprint import pprint

def init_routes(app):
    @app.route('/programs', methods=['GET'])
    def get_all_programs():
        """Récupère tous les programmes actifs"""
        programs = program_dao.get_all_programs()
        response = jsonify(programs)
        return add_cache_headers(response, max_age=900)  # 15 minutes
    
    @app.route('/programs/<string:program_id>', methods=['GET'])
    def get_program_by_id(program_id):
        """Récupère un programme par son ID"""
        program = program_dao.get_program_by_id(program_id)
        if program:
            response = jsonify(program)
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        return jsonify({"error": "Program not found"}), 404
    
    @app.route('/programs/slug/<string:slug>', methods=['GET'])
    def get_program_by_slug(slug):
        """Récupère un programme par son slug"""
        program = program_dao.get_program_by_slug(slug)
        if program:
            response = jsonify(program)
            return add_cache_headers(response, max_age=1800)  # 30 minutes
        return jsonify({"error": "Program not found"}), 404
    
    @app.route('/programs/slugs', methods=['GET'])
    def get_all_program_slugs():
        """Récupère tous les slugs des programmes (pour génération statique)"""
        slugs = program_dao.get_all_program_slugs()
        response = jsonify(slugs)
        return add_cache_headers(response, max_age=3600)  # 1 heure
    
    @app.route('/programs/by-school/<string:school_id>', methods=['GET'])
    def get_programs_by_school_id(school_id):
        """Récupère tous les programmes d'une école par ID"""
        programs = program_dao.get_programs_by_school_id(school_id)
        response = jsonify(programs)
        return add_cache_headers(response, max_age=1800)  # 30 minutes
    
    @app.route('/programs/by-school-slug/<string:school_slug>', methods=['GET'])
    def get_programs_by_school_slug(school_slug):
        """Récupère tous les programmes d'une école par slug"""
        programs = program_dao.get_programs_by_school_slug(school_slug)
        response = jsonify(programs)
        return add_cache_headers(response, max_age=1800)  # 30 minutes
    
    @app.route('/programs/<string:program_id>/similar', methods=['GET'])
    def get_similar_programs(program_id):
        """Récupère les programmes similaires"""
        limit = request.args.get('limit', 3, type=int)
        similar_programs = program_dao.get_similar_programs(program_id, limit)
        response = jsonify(similar_programs)
        return add_cache_headers(response, max_age=1800)  # 30 minutes
    
    @app.route('/programs/preview', methods=['GET'])
    def get_programs_preview():
        """Récupère un aperçu des programmes (données limitées)"""
        programs = program_dao.get_all_programs()
        # Simplifier les données pour l'aperçu
        preview = []
        for program in programs:
            preview_data = {
                'id': program['id'],
                'slug': program['slug'],
                'school_slug': program.get('school', {}).get('slug', ''),
                'name': program['name'],
                'school_name': program['school_name'],
                'grade': program['grade'],
                'fi_school_duration': program['fi_school_duration'],
                'tuition': program['tuition'],
                'alternance_possible': program.get('ca_school_duration') is not None,
                'sub_domain1_id': program['sub_domain1_id'],
                'sub_domain2_id': program['sub_domain2_id'],
                'sub_domain3_id': program['sub_domain3_id']
            }
            preview.append(preview_data)
        
        response = jsonify(preview)
        return add_cache_headers(response, max_age=900)  # 15 minutes
    
    @app.route('/programs/search', methods=['POST'])
    def search_programs():
        """Recherche de programmes avec pagination et nouveaux filtres"""
        try:
            data = request.json or {}
            filters = data.copy()
            
            # Extraire les paramètres de pagination
            page = filters.pop('page', 1)
            limit = filters.pop('limit', 12)
            
            # ✅ EXTRAIRE LES NOUVEAUX FILTRES CAMPUS FRANCE
            campus_france_filters = filters.pop('campus_france_filters', {})
            
            # Ajouter aux filtres principaux
            if campus_france_filters.get('connected'):
                filters['campus_france_connected'] = True
            
            if campus_france_filters.get('parallelProcedure'):
                filters['parallel_procedure'] = True
            
            if campus_france_filters.get('exoneration') is not None:
                filters['exoneration'] = campus_france_filters['exoneration']
            
            if campus_france_filters.get('bienvenueFrance'):
                filters['bienvenue_france_level'] = campus_france_filters['bienvenueFrance']
            
            # Valider les paramètres
            try:
                page = max(1, int(page))
                limit = max(1, min(50, int(limit)))
            except (ValueError, TypeError):
                page, limit = 1, 12
            
            print(f"🔎 Filters after processing: {filters}")
            
            # Utiliser la méthode paginée
            result = program_dao.search_programs_paginated(filters, page, limit)
            
            return jsonify(result)
        
        except Exception as e:
            print(f"❌ Error in search_programs: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e), "success": False}), 500
    
    @app.route('/programs/stats', methods=['GET'])
    def get_programs_stats():
        """Récupère les statistiques des programmes"""
        total_programs = program_dao.get_programs_count()
        response = jsonify({
            'total_programs': total_programs
        })
        return add_cache_headers(response, max_age=900)  # 15 minutes
    
    @app.route('/programs/filter-options', methods=['GET'])
    def get_program_filter_options():
        """Récupère toutes les options disponibles pour les filtres (AVEC CACHE)"""
        try:
            # Utiliser la version cachée
            options = get_cached_filter_options()
            response = jsonify(options)
            
            # Ajouter headers de cache HTTP
            return add_cache_headers(response, max_age=900)  # 15 minutes
        except Exception as e:
            print(f"❌ Error in get_program_filter_options: {e}")
            return jsonify({"error": "Internal server error"}), 500
