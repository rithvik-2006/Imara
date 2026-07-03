import uuid
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.extensions import db

class HazardEvent(db.Model):
    """
    Represents an active or past hazard event (e.g., flood, drought, locusts) mapped via a polygon.
    """
    __tablename__ = 'hazard_events'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hazard_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    # Using Polygon to represent the affected area on the map
    geom = db.Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<HazardEvent {self.hazard_type} ({self.severity})>"
