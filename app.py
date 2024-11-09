from flask import Flask, jsonify, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from urllib.parse import quote
import pymysql
from flask_migrate import Migrate
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from sqlalchemy import event
import ssl
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Install PyMySQL as MySQL driver
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# CORS configuration
CORS(app)
# CORS(app, 
#      origins=["http://localhost:3000"],
#      supports_credentials=True)

# Security configurations
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_SORT_KEYS'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://u963469710_wendogo:%s@89.117.169.204/u963469710_wendogo' % quote('Support001@')


# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#     'pool_size': 10,
#     'pool_recycle': 280,
#     'pool_pre_ping': True,
#     'connect_args': {
#         'ssl': False,
#         'charset': 'utf8mb4',
#         'use_unicode': True,
#         'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'
#     }
# }

# Import models
from common.models import db

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Error handler for database errors
@app.errorhandler(SQLAlchemyError)
def handle_db_error(error):
    logger.error(f"Database error occurred: {str(error)}")
    return jsonify({"error": "Database error occurred", "details": str(error)}), 500

# Add request logging middleware
@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

# Function to set up SQL query logging
def setup_sql_logging(app):
    @event.listens_for(db.engine, 'before_cursor_execute')
    def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
        logger.debug("SQL Statement: %s", statement)
        logger.debug("Parameters: %s", params)

# Setup database and import models
with app.app_context():
    try:
        from common.models import *
        logger.info('Initializing database...')
        db.create_all()
        # Set up SQL logging within app context
        setup_sql_logging(app)
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Import routes
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
    major_route,
    school_route
)

def register_routes(app):
    try:
        routes = [
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
            major_route,
            school_route
        ]
        
        for route in routes:
            route.init_routes(app)
    except Exception as e:
        logger.error(f"Error registering routes: {str(e)}")
        raise

register_routes(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
