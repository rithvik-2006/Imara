import uuid
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.extensions import db

class Community(db.Model):
    """
    Represents a farming community that will receive early warning alerts.
    """
    __tablename__ = 'communities'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    # SRID 4326 denotes the WGS 84 spatial reference system (standard GPS coordinates)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    preferred_language = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

    primary_livelihood = db.Column(db.String(100), nullable=True)
    population = db.Column(db.Integer, nullable=True)
    vulnerability_score = db.Column(db.Float, nullable=True)
    district = db.Column(db.String(100), nullable=True)
    preferred_channel = db.Column(db.String(50), nullable=True, default='SMS')
    preferred_alert_time = db.Column(db.String(50), nullable=True)
    last_alert_sent = db.Column(db.DateTime, nullable=True)
    risk_level = db.Column(db.String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<Community {self.name}>"
