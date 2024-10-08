from flask import jsonify
from common.daos.spoken_language_dao import spoken_language_dao

def init_routes(app):
    @app.route('/spokenlanguages', methods=['GET'])
    def get_all_spoken_languages():
        spoken_languages = spoken_language_dao.get_all()
        return jsonify(spoken_languages)
