from flask import jsonify
from common.daos.city_dao import cities_dao

def init_routes(app):
    @app.route('/cities', methods=['GET'])
    def get_all_cities():
        cities = cities_dao.get_all()
        return jsonify(cities)

    @app.route('/cities/<string:iso2>', methods=['GET'])
    def get_cities_by_country_iso2(iso2):
        cities = cities_dao.get_cities_by_country_iso2(iso2)
        return jsonify(cities)
