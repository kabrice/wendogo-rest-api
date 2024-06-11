from flask import jsonify
from common.daos.lead_status_dao import lead_status_dao
from common.models.lead_status import LeadStatus
#from . import routes
#from app import app

def init_routes(app):
    @app.route('/leadstatus', methods=['GET'])
    def get_lead_status():
        print('##### get_lead_status')
        #users = []
        lead_status = lead_status_dao.get_all()
        #users = users_schema.dump(data)
        return jsonify(lead_status)
