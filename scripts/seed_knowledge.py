import os
import sys

# Ensure app can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.knowledge_document import KnowledgeDocument
from app.services.retrieval_service import RetrievalService

def seed_knowledge():
    app = create_app()
    with app.app_context():
        # Check if already seeded
        if KnowledgeDocument.query.count() > 0:
            print("Knowledge base already seeded.")
            return

        print("Seeding humanitarian knowledge documents...")
        
        sample_docs = [
            {
                "title": "WHO Flood Preparedness Guide",
                "category": "Flood",
                "source": "WHO Manual",
                "text": "In the event of severe flooding, livestock farmers should immediately move animals to higher ground. Do not attempt to cross flooded areas with livestock. Ensure clean drinking water is available as floodwaters are contaminated."
            },
            {
                "title": "FAO Agriculture Drought Guide",
                "category": "Drought",
                "source": "FAO Agriculture Guides",
                "text": "During prolonged drought, prioritize drought-resistant crops. Ration water for livestock and provide shade. Farmers should consider early harvesting if crops are mature enough to avoid total loss."
            },
            {
                "title": "Cyclone Safety for Communities",
                "category": "Cyclone",
                "source": "Red Cross",
                "text": "When a cyclone approaches, secure all loose outdoor items. Stay indoors in the strongest part of the building. Keep emergency kits ready including flashlights, batteries, and first-aid supplies."
            },
            {
                "title": "Livestock Safety during Heatwaves",
                "category": "Heatwave",
                "source": "Veterinary Services",
                "text": "Provide ample shade and cool, fresh water at all times for livestock during extreme heat. Avoid transporting animals during the hottest parts of the day to prevent heat stroke."
            }
        ]

        retrieval_service = RetrievalService()
        
        docs_to_insert = []
        for doc_data in sample_docs:
            doc = KnowledgeDocument(
                title=doc_data['title'],
                category=doc_data['category'],
                source=doc_data['source'],
                text=doc_data['text'],
                embedding_created=True
            )
            db.session.add(doc)
            db.session.flush() # To get the ID
            
            docs_to_insert.append({
                "id": str(doc.id),
                "title": doc.title,
                "category": doc.category,
                "text": doc.text
            })

        db.session.commit()
        
        print(f"Embedding {len(docs_to_insert)} documents and adding to vector store...")
        retrieval_service.add_documents(docs_to_insert)
        
        print("Knowledge base seeded successfully.")

if __name__ == "__main__":
    seed_knowledge()
