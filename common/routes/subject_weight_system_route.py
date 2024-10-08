from flask import jsonify
from common.daos.subject_weight_system_dao import subject_weight_system_dao

def init_routes(app):
    @app.route('/subjectWeightSystems', methods=['GET'])
    def get_all_subject_weight_systems():
        subject_weight_systems = subject_weight_system_dao.get_all()
        return jsonify(subject_weight_systems)
