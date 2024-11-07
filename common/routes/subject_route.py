from flask import jsonify
from common.services.subject_service import subject_service
from common.daos.subject_dao import subject_dao

def init_routes(app):
    #Todo Later: manager userid to update user level value"""
    @app.route('/subjectmatches/search/<string:external_subject_input>', methods=['GET'])
    def get_search_subject_matches_from_user_input_(external_subject_input):
        subject_similarities = subject_service.get_search_subject_matches_from_user_input1(external_subject_input)
        return jsonify(subject_similarities)
    
    #Todo Later: manager userid to update user level value"""
    @app.route('/subject/search/<string:applying_for_master>/<string:external_subject_input>', methods=['GET'])
    def get_search_subject_matches_by_level_id(applying_for_master, external_subject_input):
        applying_for_master = applying_for_master.lower() == 'true'
        print(f'🥶 applying_for_master: {applying_for_master} and external_subject_input: {external_subject_input}')
        subject_similarities = subject_service.get_search_subject_matches_from_user_input(applying_for_master, external_subject_input)
        return jsonify(subject_similarities)

