from flask import jsonify
from common.daos.level_dao import level_dao

def init_routes(app):
    @app.route('/level/highschools', methods=['GET'])
    def get_high_school_levels():
        levels = level_dao.get_high_school_levels()
        return jsonify(levels)
    @app.route('/level/degrees/<string:bac_id>', methods=['GET'])
    def get_degree_by_bac_id(bac_id):
        degrees = level_dao.get_degree_by_bac_id(bac_id)
        return jsonify(degrees)
