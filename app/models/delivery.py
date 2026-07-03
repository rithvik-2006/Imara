import uuid
from datetime import datetime, timezone
from app.extensions import db

class DeliveryLog(db.Model):
    """
    Tracks the delivery status of SMS and Voice payloads sent via Africa's Talking.
    """
    __tablename__ = 'delivery_logs'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    community_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('communities.id'), nullable=False)
    channel = db.Column(db.String(50), nullable=False) # 'SMS', 'VOICE', 'USSD'
    status = db.Column(db.String(50), nullable=False, default='Pending') # 'Pending', 'Sent', 'Delivered', 'Failed'
    message_id = db.Column(db.String(100), nullable=True) # Africa's Talking reference ID
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    community = db.relationship('Community', backref=db.backref('deliveries', lazy=True))

    def __repr__(self):
        return f"<DeliveryLog {self.channel} - {self.status}>"
