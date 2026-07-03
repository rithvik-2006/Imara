from app import create_app
from app.extensions import celery

app = create_app()
# The celery object is already configured in create_app
app.app_context().push()
