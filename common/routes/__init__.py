from flask import Blueprint
routes = Blueprint('routes', __name__)

from .lead_status_route import *
