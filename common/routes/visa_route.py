from flask import jsonify
from common.services.visa_service import visa_service

def init_routes(app):
    #@app.route('/visa', methods=['GET'])
    
    @app.route('/visatypes/country/<string:country_iso2>', methods=['GET'])
    def get_visa_by_country_name(country_iso2):
        visa_types = visa_service.get_visatypes_by_country_iso2(country_iso2)
        return jsonify(visa_types)  
    
