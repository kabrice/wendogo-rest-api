from flask import jsonify
from common.services.subject_service import subject_service
from common.daos.subject_dao import subject_dao

def init_routes(app):
    #Todo Later: manager userid to update user level value"""
    @app.route('/subject/search/<string:external_subject_input>', methods=['GET'])
    def get_search_subject_matches_from_user_input(external_subject_input):
        subject_similarities = subject_service.get_search_subject_matches_from_user_input(external_subject_input)
        return jsonify(subject_similarities)

