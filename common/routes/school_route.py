from flask import request, jsonify, json
from common.daos.school_dao import school_dao

def init_routes(app):
    @app.route('/schools/filtring', methods=['POST'])
    def get_school_details_from_school_ids():
        school_ids = request.json.get('school_ids') #['sch0095', 'sch0140', 'sch0146', 'sch0172', 'sch0195', etc]
        school_details = school_dao.get_schools_from_ids(school_ids)
        return jsonify(school_details)
