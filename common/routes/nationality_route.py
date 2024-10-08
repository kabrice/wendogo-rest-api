from flask import jsonify
from common.daos.nationality_dao import nationality_dao

def init_routes(app):
    @app.route('/nationalities', methods=['GET'])
    def get_all_nationalities():
        nationalities = nationality_dao.get_all_nationalities()
        return jsonify(nationalities)
