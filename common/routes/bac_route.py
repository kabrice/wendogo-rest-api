from flask import jsonify
from common.daos.bac_dao import bac_dao

def init_routes(app):
    @app.route('/bac/universities', methods=['GET'])
    def get_bacs_of_university():
        bacs = bac_dao.get_bacs_of_university()
        return jsonify(bacs)
