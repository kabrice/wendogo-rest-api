from flask import jsonify
from common.daos.degree_dao import degree_dao

def init_routes(app):
    @app.route('/degrees/<string:type_of_school>', methods=['GET']) #type_of_school: 'university' or 'highschool'
    def get_degrees(type_of_school):
        if type_of_school == 'highschool':
            degrees = degree_dao.get_degree_by_id_list([ 'deg00003'])
        elif type_of_school == 'university':
            degrees = degree_dao.get_degree_by_not_in_id_list(['deg00001', 'deg00002', 'deg00003', ''])
        return jsonify(degrees)
