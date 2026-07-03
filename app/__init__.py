import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from app.extensions import db

def create_app() -> Flask:
    """
    Factory function to create the Flask application instance.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app) # Allow Next.js frontend to access APIs
    
    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register API routes blueprint
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from app.routes.communication import communication_bp
    app.register_blueprint(communication_bp, url_prefix='/api/v1')
    
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    
    return app
