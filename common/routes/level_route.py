from flask import jsonify
from common.daos.level_dao import level_dao

def init_routes(app):
    @app.route('/level/highschools', methods=['GET'])
    def get_high_school_levels():
        levels = level_dao.get_high_school_levels()
        return jsonify(levels)
