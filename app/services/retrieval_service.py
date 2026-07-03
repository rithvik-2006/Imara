import logging
from typing import List, Dict, Any
from app.services.embedding_service import EmbeddingService
from app.vectorstore.faiss_store import FaissStore

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = FaissStore()
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        documents format: [{'id': 'doc_id', 'text': 'content', ...}]
        """
        texts = [doc['text'] for doc in documents]
        embeddings = self.embedding_service.embed_batch(texts)
        if embeddings:
            self.vector_store.add_embeddings(embeddings, documents)

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves relevant context for a given query to inject into prompts.
        """
        try:
            query_embedding = self.embedding_service.embed_text(query)
            results = self.vector_store.search(query_embedding, top_k=top_k)
            
            if not results:
                return ""
                
            contexts = []
            for meta, distance in results:
                contexts.append(f"- {meta.get('text', '')}")
                
            return "\n".join(contexts)
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
