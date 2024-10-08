from flask import jsonify
from common.services.level_value_service import level_value_service
from common.daos.level_value_dao import level_value_dao

def init_routes(app):
    #Todo Later: manager userid to update user level value"""
    @app.route('/levelvalue/<string:userid>/<string:external_level_value_input>', methods=['GET'])
    def get_best_level_value_match_from_user_input(userid, external_level_value_input):
        best_match, best_similarity = level_value_service.get_best_level_value_match_from_user_input(external_level_value_input)
        return jsonify({'best_match': best_match, 'best_similarity': best_similarity})
    
    @app.route('/levelvalue/search/<string:external_level_value_input>', methods=['GET'])
    def get_search_level_value_matches_from_user_input(external_level_value_input):
        level_value_similarities = level_value_service.get_search_level_value_matches_from_user_input(external_level_value_input)
        return jsonify(level_value_similarities)
    
    @app.route('/levelvalue/all', methods=['GET'])
    def get_all_level_values():
        level_values = level_value_dao.get_all()
        return jsonify(level_values)
