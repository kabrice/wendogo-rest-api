import sys
from flask import Flask, jsonify, request, current_app
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
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
from common.utils.cache_decorator import init_cache_middleware, CacheManager
from dotenv import load_dotenv 
from pathlib import Path
# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


logger.info("🚀 Chargement .env...")
load_dotenv()
logger.info("✅ .env chargé")

# --- Debug valeurs env ---
logger.info("🔍 ENV VARIABLES")
logger.info(f"MAIL_SERVER = {os.getenv('MAIL_SERVER')}")
logger.info(f"MAIL_USERNAME = {os.getenv('MAIL_USERNAME')}")
logger.info(f"MAIL_PASSWORD = {'***' if os.getenv('MAIL_PASSWORD') else None}")
logger.info(f"MAIL_DEFAULT_SENDER = {os.getenv('MAIL_DEFAULT_SENDER')}")

# --- Vérification du .env ---
cwd = os.getcwd()
env_path = os.path.join(cwd, ".env")
logger.info(f"Working directory: {cwd}")
logger.info(f".env present at {env_path}? {os.path.exists(env_path)}")
if os.path.exists(env_path):
    try:
        with open(env_path, "r") as f:
            content = f.read().strip().splitlines()
            logger.info("Contenu .env (tronc.):")
            for line in content[:10]:
                logger.info(f"> {line}")
    except Exception as e:
        logger.error(f"Impossible de lire .env : {e}")
else:
    logger.warning(".env introuvable dans le répertoire courant")


# Install PyMySQL as MySQL driver
pymysql.install_as_MySQLdb()

mail = Mail() 
app = Flask(__name__)

# CORS configuration
CORS(app, 
     origins=["https://wendogo.com", "https://www.wendogo.com"],
     supports_credentials=True,
     allow_headers=[
         "Content-Type", 
         "Authorization", 
         "X-Requested-With",
         "Accept"
     ],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"]
)
# CORS(app, 
#      origins=["https://wendogo.com", "https://www.wendogo.com"],
#      supports_credentials=True,  # ✅ OBLIGATOIRE pour les cookies/tokens
#      allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
#      methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
# )
#CORS(app)
# CORS(app, 
#      origins=["http://localhost:3000"],
#      supports_credentials=True)

# Security configurations
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_SORT_KEYS'] = False

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Configuration email (ajoutez à app.py)
# Configuration email en dur (pour production temporaire)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] =  os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['DEBUG'] = True

# Clé secrète pour JWT (en dur aussi)
app.config['SECRET_KEY'] = '7453dd43ba0aa8721a2bef0bea69e61e'

mail.init_app(app)
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

# ✅ NOUVEAU: Initialiser le middleware de cache
init_cache_middleware(app)


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
        
        # ✅ NOUVEAU: Préchauffer le cache au démarrage
        logger.info('Warming up cache...')
        CacheManager.warm_up()
        logger.info('Cache warmed up successfully')
        
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
    school_route,
    domain_route,
    subdomain_route,
    program_route,
    stats_route,
    auth_route,
    user_favorites_route,
    user_dashboard_route,
    test_auth_route,
    accompany_route,
    admin_auth_route,
    admin_password_manager_route,
    cache_admin_route,
    contact_route,
    admin_contact_route
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
            school_route,
            domain_route,
            subdomain_route,
            program_route,
            stats_route,
            auth_route,
            user_favorites_route,
            user_dashboard_route,
            test_auth_route,
            accompany_route,
            admin_auth_route,
            admin_password_manager_route,
            cache_admin_route,
            contact_route,
            admin_contact_route
        ]
        
        for route in routes:
            route.init_routes(app)
    except Exception as e:
        logger.error(f"Error registering routes: {str(e)}")
        raise

register_routes(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
