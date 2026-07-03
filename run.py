from app import create_app
from app.extensions import db
from flask_migrate import Migrate
from app.models.community import Community
from app.models.hazard_event import HazardEvent

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Exposes database instances to the flask shell for debugging."""
    return {'db': db, 'Community': Community, 'HazardEvent': HazardEvent}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
