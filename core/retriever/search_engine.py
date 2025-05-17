from typing import List, Optional
import faiss
import numpy as np
import os

class SearchEngine:
    """Engine for performing vector similarity search."""
    
    def __init__(self, vector_db_path: str, top_k: int = 3, embedding_dim: int = 768):
        """Initialize the search engine.
        
        Args:
            vector_db_path (str): Path to the FAISS index
            top_k (int): Number of results to return
            embedding_dim (int): Dimension of embeddings
        """
        self.vector_db_path = vector_db_path
        self.top_k = top_k
        self.embedding_dim = embedding_dim
        
        if not os.path.exists(vector_db_path):
            # Create a new empty index if one doesn't exist
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.save()
        else:
            self.index = faiss.read_index(vector_db_path)
            # Check if dimensions match
            if self.index.d != embedding_dim:
                print(f"Warning: Index dimension ({self.index.d}) doesn't match expected dimension ({embedding_dim}).")
                print("Using the index's dimension for compatibility.")
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text.
        Currently a placeholder - you should replace this with your
        preferred embedding model (e.g. OpenAI, SBERT, etc.)
        
        Args:
            text (str): The text to embed
            
        Returns:
            np.ndarray: The text embedding
        """
        # Placeholder: Replace with actual embedding logic
        # Should return a vector of shape (1, embedding_dim)
        dim = self.index.d  # Get dimension from index
        return np.random.randn(1, dim).astype('float32')
    
    def search(self, query: str, k: Optional[int] = None) -> List[str]:
        """Search for documents relevant to a query.
        
        Args:
            query (str): The search query
            k (Optional[int]): Override default number of results
            
        Returns:
            List[str]: List of relevant document chunks
        """
        if self.index.ntotal == 0:
            return []
            
        k = k or self.top_k
        k = min(k, self.index.ntotal)  # Don't request more items than we have
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Search index
        distances, indices = self.index.search(query_embedding, k)
        
        # Placeholder: In a real implementation, you would:
        # 1. Map indices back to actual document chunks
        # 2. Maybe filter by distance threshold
        # 3. Return the actual text chunks
        # For now, we just return a placeholder list
        return [
            f"Document chunk {i} (distance: {d:.3f})"
            for i, d in zip(indices[0], distances[0])
        ]
    
    def add_document(self, document: str) -> None:
        """Add a single document to the index.
        
        Args:
            document (str): The document to add
        """
        embedding = self._get_embedding(document)
        self.index.add(embedding)
        self.save()
        
    def add_documents(self, documents: List[str]) -> None:
        """Add multiple documents to the index.
        
        Args:
            documents (List[str]): The documents to add
        """
        embeddings = np.vstack([
            self._get_embedding(doc) for doc in documents
        ])
        self.index.add(embeddings)  
        self.save()
        
    def save(self) -> None:
        """Save the index to disk."""
        try:
            faiss.write_index(self.index, self.vector_db_path)
        except Exception as e:
            print(f"Error saving index: {str(e)}")