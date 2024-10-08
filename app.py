from flask import Flask 
from flaskext.mysql import MySQL
from flask_cors import CORS 
from urllib.parse import quote
from sqlalchemy.pool import QueuePool
import ssl
from flask_migrate import Migrate

#ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
#ctx.load_cert_chain('certificate.pem', 'privateKey.pem')

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:3000"]) # For development
#CORS(app) # For production
#app.config['SECRET_KEY'] = 'top-secret!'

from common.models import db

#db = SQLAlchemy(engine_options={"pool_size": 10, 'pool_recycle': 280, "poolclass":QueuePool, "pool_pre_ping":True})
#ma = Marshmallow()

mysql =MySQL()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://u963469710_wendogo:%s@89.117.169.204/u963469710_wendogo' % quote('Support001@')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/wendogo'
# from common.routes import lead_status_route
# app.register_blueprint(lead_status_route)

# @app.route('/')
# def index():    
#     return jsonify({"message": "Hello World"})

db.init_app(app)
with app.app_context():
    from common.models import *
    migrate = Migrate(app, db)
    print('db being created')
    db.create_all()
    
from common.routes import (
    lead_status_route,
    user_route,
    lead_route,
    visa_route,
    school_year_route,
    level_route,
    bac_route,
    country_route,
    degree_route,
    level_value_route,
    subject_route,
    city_route,
    spoken_language_route,
    academic_year_organization_route,
    mark_system_route,
    subject_weight_system_route,
    nationality_route,
)
    
lead_status_route.init_routes(app)
user_route.init_routes(app)
lead_route.init_routes(app)
visa_route.init_routes(app)
school_year_route.init_routes(app)
level_route.init_routes(app)
bac_route.init_routes(app)
country_route.init_routes(app)
degree_route.init_routes(app)
level_value_route.init_routes(app)
subject_route.init_routes(app)
city_route.init_routes(app)
spoken_language_route.init_routes(app)
academic_year_organization_route.init_routes(app)
mark_system_route.init_routes(app)
subject_weight_system_route.init_routes(app)
nationality_route.init_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
