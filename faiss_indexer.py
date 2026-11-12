import re
import numpy as np
import faiss
from typing import List, Dict, Any

class FAISSContractIndexer:
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.metadata: List[Dict[str, Any]] = []

    def _embed_text(self, text: str) -> np.ndarray:
        """
        Generates a normalized deterministic dense embedding vector
        based on token hashing and n-gram term frequencies.
        """
        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        words = re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())
        
        if not words:
            return vec

        for w in words:
            # Word level hash
            h1 = hash(w) % self.embedding_dim
            vec[h1] += 1.0
            
            # Character trigram level hash for fuzzy semantic match
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    trigram = w[i:i+3]
                    h2 = hash(trigram) % self.embedding_dim
                    vec[h2] += 0.5

        # L2 normalize vector for cosine inner-product search
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def index_contracts(self, contracts: Dict[str, str]) -> int:
        """
        Chunks contracts into clauses, generates FAISS vectors, and indexes them.
        """
        chunks = []
        chunk_metas = []
        
        for doc_name, text in contracts.items():
            # Split by double newline or section markers
            raw_clauses = re.split(r"\n\s*\n|(?=SECTION\s+\d+)", text, flags=re.IGNORECASE)
            
            for c in raw_clauses:
                cleaned = c.strip()
                if len(cleaned) < 20:
                    continue
                    
                chunks.append(cleaned)
                chunk_metas.append({
                    "contract_name": doc_name,
                    "clause_text": cleaned
                })

        if not chunks:
            return 0

        # Build numpy matrix of embeddings
        matrix = np.zeros((len(chunks), self.embedding_dim), dtype=np.float32)
        for i, c in enumerate(chunks):
            matrix[i] = self._embed_text(c)

        self.index.reset()
        self.index.add(matrix)
        self.metadata = chunk_metas
        return len(chunks)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Queries FAISS vector index and returns top matching clauses with metadata.
        """
        if self.index.ntotal == 0:
            return []

        query_vec = self._embed_text(query).reshape(1, -1)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)
        
        results = []
        for i in range(k):
            idx = int(indices[0][i])
            if idx >= 0 and idx < len(self.metadata):
                item = dict(self.metadata[idx])
                item["similarity_score"] = float(scores[0][i])
                results.append(item)
                
        return results

