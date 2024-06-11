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
        


   