import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

class VectorStore:
    def __init__(self, data_path="data/interior_design_dataset.json"):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.data_path = data_path
        self.records = []
        self.index = None
        self.load_and_index()

    def load_and_index(self):
        """Load records from JSON and create a FAISS index."""
        try:
            with open(self.data_path, 'r') as f:
                self.records = json.load(f)
            
            # Combine task and struggle for embedding
            texts = [f"{r['task']} {r['struggle']}" for r in self.records]
            embeddings = self.model.encode(texts)
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))
        except Exception as e:
            print(f"Error loading vector store: {e}")

    def search(self, query, top_k=3):
        """Search for the most relevant records in the vector store."""
        if not self.index:
            return []
        
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.records):
                results.append(self.records[idx])
        return results
