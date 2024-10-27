from flask import request, jsonify, json
from common.daos.major_dao import major_dao

def init_routes(app):
    @app.route('/majors/filtring', methods=['POST'])
    def get_major_details_from_major_ids():
        major_ids = request.json.get('major_ids') #['maj0095', 'maj0140', 'maj0146', 'maj0172', 'maj0195', etc]
        major_details = major_dao.get_major_subdomains_from_ids(major_ids)
        return jsonify(major_details)
