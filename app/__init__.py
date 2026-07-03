import os
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from app.extensions import db, celery

def celery_init_app(app: Flask) -> celery:
    class FlaskTask(celery.Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = celery
    celery_app.config_from_object('celeryconfig')
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    celery_app.Task = FlaskTask
    return celery_app

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
    
    # Initialize Celery
    app.config.from_mapping(
        CELERY=dict(
            broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
            task_ignore_result=True,
        ),
    )
    celery_init_app(app)    
    # Register API routes blueprint
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from app.routes.communication import communication_bp
    app.register_blueprint(communication_bp, url_prefix='/api/v1')
    
    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1/dashboard')
    
    return app
