import uuid
from datetime import datetime, timezone
from app.extensions import db

class KnowledgeDocument(db.Model):
    """
    Stores metadata for RAG documents.
    """
    __tablename__ = 'knowledge_documents'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(255), nullable=True)
    text = db.Column(db.Text, nullable=False)
    embedding_created = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<KnowledgeDocument {self.title}>"
