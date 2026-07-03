from flask_sqlalchemy import SQLAlchemy
from celery import Celery

# Initialize SQLAlchemy with no app context yet
db = SQLAlchemy()

# Initialize Celery with no app context yet
celery = Celery(__name__)
