from flask import request, jsonify
from common.daos.lead_dao import lead_dao
from common.models import db
from common.models.lead import Lead
from common.models.log import Log
from common.helper import Helper


def init_routes(app):

    @app.route('/lead/add', methods=['POST'])
    def add_lead():
        _json = request.json
        new_lead = Lead()
        for key in _json:
            setattr(new_lead, key, _json[key] if (key in _json) else '')
        db.session.add(new_lead)
        db.session.commit()
        return jsonify({"status": True, "message": "lead has been added"})
    
    @app.route('/lead/update/clicks', methods=['PUT'])
    def update_clicks_and_project_message_by_user_id():
        _json = request.json 
        user_id = int(_json['userId'])
        lead = lead_dao.get_by_user_id(user_id)
        lead.contacted_clicks += 1
        lead.project_message = _json['projectMessage']
        db.session.commit()
        return jsonify({"status": True, "message": "lead has been updated"})



   