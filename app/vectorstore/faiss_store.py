import os
import faiss
import numpy as np
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class FaissStore:
    def __init__(self, index_path="faiss_index.bin", dimension=384):
        self.index_path = index_path
        self.dimension = dimension
        
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
            except Exception as e:
                logger.error(f"Failed to read index, creating new: {e}")
                self.index = faiss.IndexFlatL2(self.dimension)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            
        # Metadata store: map FAISS ID to Document ID
        self.metadata = {}

    def add_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        if not embeddings:
            return
            
        vectors = np.array(embeddings).astype('float32')
        start_id = self.index.ntotal
        
        self.index.add(vectors)
        faiss.write_index(self.index, self.index_path)
        
        for i, meta in enumerate(metadata):
            self.metadata[start_id + i] = meta

    def search(self, query_embedding: List[float], top_k=5) -> List[Tuple[Dict[str, Any], float]]:
        if self.index.ntotal == 0 or not query_embedding:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, top_k)
        
        results = []
        for j, i in enumerate(indices[0]):
            if i != -1 and i in self.metadata:
                results.append((self.metadata[i], float(distances[0][j])))
                
        return results
