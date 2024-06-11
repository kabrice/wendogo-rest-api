from flask import jsonify
from common.daos.school_year_dao import school_year_dao

def init_routes(app):
    @app.route('/schoolyear', methods=['GET'])
    def get_school_year():
        school_year = school_year_dao.get_all()
        return jsonify(school_year)
