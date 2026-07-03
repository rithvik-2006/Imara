import uuid
from datetime import datetime, timezone
from app.extensions import db

class AlertJob(db.Model):
    """
    Tracks the state of asynchronous alert processing.
    """
    __tablename__ = 'alert_jobs'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('communities.id'), nullable=False)
    hazard_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('hazard_events.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Queued') # 'Queued', 'Processing', 'Completed', 'Failed'
    worker_id = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    processing_time = db.Column(db.Float, nullable=True)
    ai_latency = db.Column(db.Float, nullable=True)
    translation_latency = db.Column(db.Float, nullable=True)
    tts_latency = db.Column(db.Float, nullable=True)
    sms_latency = db.Column(db.Float, nullable=True)
    voice_latency = db.Column(db.Float, nullable=True)
    
    error_message = db.Column(db.Text, nullable=True)

    community = db.relationship('Community', backref=db.backref('alert_jobs', lazy=True))
    hazard = db.relationship('HazardEvent', backref=db.backref('alert_jobs', lazy=True))

    def __repr__(self):
        return f"<AlertJob {self.id} - {self.status}>"
