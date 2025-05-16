import os
from typing import List, Optional
import numpy as np
import faiss
from langchain_text_splitters import TokenTextSplitter

class IndexBuilder:
    """Builder for creating and maintaining the vector search index."""
    
    def __init__(self, vector_db_path: str, embedding_dim: int = 768):
        """Initialize the index builder.
        
        Args:
            vector_db_path (str): Path to store the FAISS index
            embedding_dim (int): Dimension of document embeddings
        """
        self.vector_db_path = vector_db_path
        self.embedding_dim = embedding_dim
        self.text_splitter = TokenTextSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
        
        # Create or load the index
        self.index = self._load_or_create_index()
        
    def _load_or_create_index(self) -> faiss.Index:
        """Load existing index or create a new one.
        
        Returns:
            faiss.Index: The FAISS index
        """
        if os.path.exists(self.vector_db_path):
            return faiss.read_index(self.vector_db_path)
        else:
            index = faiss.IndexFlatL2(self.embedding_dim)
            faiss.write_index(index, self.vector_db_path)
            return index
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for a list of texts.
        Currently a placeholder - you should replace this with your
        preferred embedding model (e.g. OpenAI, SBERT, etc.)
        
        Args:
            texts (List[str]): The texts to embed
            
        Returns:
            np.ndarray: The embeddings matrix
        """
        # Placeholder: Replace with actual embedding logic
        # Should return a matrix of shape (len(texts), self.embedding_dim)
        return np.random.randn(len(texts), self.embedding_dim).astype('float32')
    
    def add_document(self, content: str, metadata: Optional[dict] = None) -> None:
        """Add a document to the index.
        
        Args:
            content (str): The document content
            metadata (Optional[dict]): Document metadata
        """
        # Split document into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Get embeddings
        embeddings = self._get_embeddings(chunks)
        
        # Add to index
        self.index.add(embeddings)
        
        # Save index
        faiss.write_index(self.index, self.vector_db_path)
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[dict]] = None) -> None:
        """Add multiple documents to the index.
        
        Args:
            documents (List[str]): List of document contents
            metadatas (Optional[List[dict]]): List of document metadata
        """
        # Process all documents
        all_chunks = []
        for doc in documents:
            chunks = self.text_splitter.split_text(doc)
            all_chunks.extend(chunks)
        
        # Get embeddings for all chunks
        embeddings = self._get_embeddings(all_chunks)
        
        # Add to index
        self.index.add(embeddings)
        
        # Save index
        faiss.write_index(self.index, self.vector_db_path)