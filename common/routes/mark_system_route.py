from flask import jsonify
from common.daos.mark_system_dao import mark_system_dao

def init_routes(app):
    @app.route('/markSystems', methods=['GET'])
    def get_all_mark_systems():
        mark_systems = mark_system_dao.get_all()
        return jsonify(mark_systems)

