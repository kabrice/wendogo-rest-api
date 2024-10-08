from flask import jsonify
from common.daos.academic_year_organization_dao import academic_year_organization_dao

def init_routes(app):
    @app.route('/academicYearOrganizations', methods=['GET'])
    def get_all_academic_year_organizations():
        academic_year_organizations = academic_year_organization_dao.get_all()
        return jsonify(academic_year_organizations)

