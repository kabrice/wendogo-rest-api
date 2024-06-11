from flask import jsonify
from common.models import db
from flask import request, jsonify, json
from sqlalchemy import text

def init_routes(app):

    @app.route('/countries/<string:default_country_iso2>', methods=['GET'])
    def get_countries_with_default_value(default_country_iso2): 
        country_res = db.session.execute(text("SELECT translations, iso2, id FROM countries"))
        data_country = []

        for row in country_res:
            #print('😅 #####rrrow', row[0])
            json_object = row[0]
            json_object = json.loads(json_object)
            #country_local = json_object['fr']
            if "fr" in json_object:
                data_country.append({'id':row[2], 'name': str(json_object["fr"]), 'iso2':row[1], 'default':row[1] == default_country_iso2})

        return data_country
    
