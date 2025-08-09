from flask import Flask
from flask_cors import CORS
import logging
import os

from app.routes.api import api
from app.dataService.utils.helpers import NpEncoder
from app.dataService.dataService import DataService


def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backend_sql_sugg.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info("Backend application starting...")

    # Create DataService Intstance
    dataService = DataService("spider")
    app.dataService = dataService

    app.json_encoder = NpEncoder
    app.register_blueprint(api, url_prefix='/api')
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    logger.info("Backend ready")
    return app
