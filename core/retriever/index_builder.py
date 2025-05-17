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
            index = faiss.read_index(self.vector_db_path)
            # If the index dimension doesn't match our expected dimension,
            # create a new index with the correct dimension
            if index.d != self.embedding_dim:
                print(f"Warning: Existing index has dimension {index.d}, but expected {self.embedding_dim}.")
                print(f"Creating a new index with dimension {self.embedding_dim}.")
                index = faiss.IndexFlatL2(self.embedding_dim)
                faiss.write_index(index, self.vector_db_path)
            return index
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
        try:
            # Skip empty content
            if not content or not content.strip():
                print("Warning: Empty content provided. Skipping document.")
                return
                
            # Split document into chunks
            chunks = self.text_splitter.split_text(content)
            
            # Skip if no chunks were created
            if not chunks:
                print(f"Warning: No chunks created from document. Skipping.")
                return
            
            # Get embeddings
            embeddings = self._get_embeddings(chunks)
            
            # Verify dimensions match
            if embeddings.shape[1] != self.index.d:
                print(f"Warning: Embedding dimension mismatch. Expected {self.index.d}, got {embeddings.shape[1]}.")
                # Resize embeddings to match index dimension
                if embeddings.shape[1] > self.index.d:
                    # Truncate to match
                    print(f"Truncating embeddings from {embeddings.shape[1]} to {self.index.d} dimensions.")
                    embeddings = embeddings[:, :self.index.d]
                else:
                    # Pad with zeros to match
                    print(f"Padding embeddings from {embeddings.shape[1]} to {self.index.d} dimensions.")
                    padding = np.zeros((embeddings.shape[0], self.index.d - embeddings.shape[1]), dtype=np.float32)
                    embeddings = np.hstack((embeddings, padding))
            
            # Add to index
            self.index.add(embeddings)
            
            # Save index
            self.save()
            
        except Exception as e:
            print(f"Error adding document to index: {str(e)}")
            # Continue without failing the entire process
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[dict]] = None) -> None:
        """Add multiple documents to the index.
        
        Args:
            documents (List[str]): List of document contents
            metadatas (Optional[List[dict]]): List of document metadata
        """
        # Filter out empty documents
        valid_docs = [doc for doc in documents if doc and doc.strip()]
        if len(valid_docs) < len(documents):
            print(f"Warning: Skipped {len(documents) - len(valid_docs)} empty documents.")
        
        if not valid_docs:
            print("Warning: No valid documents to add.")
            return
            
        try:
            # Process all documents
            all_chunks = []
            for doc in valid_docs:
                chunks = self.text_splitter.split_text(doc)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                print("Warning: No chunks created from documents. Skipping.")
                return
                
            # Get embeddings for all chunks
            embeddings = self._get_embeddings(all_chunks)
            
            # Verify dimensions match
            if embeddings.shape[1] != self.index.d:
                print(f"Warning: Embedding dimension mismatch. Expected {self.index.d}, got {embeddings.shape[1]}.")
                # Resize embeddings to match index dimension
                if embeddings.shape[1] > self.index.d:
                    # Truncate to match
                    embeddings = embeddings[:, :self.index.d]
                else:
                    # Pad with zeros to match
                    padding = np.zeros((embeddings.shape[0], self.index.d - embeddings.shape[1]), dtype=np.float32)
                    embeddings = np.hstack((embeddings, padding))
            
            # Add to index
            self.index.add(embeddings)
            
            # Save index
            self.save()
            
        except Exception as e:
            print(f"Error adding documents to index: {str(e)}")
    
    def save(self) -> None:
        """Save the index to disk."""
        try:
            faiss.write_index(self.index, self.vector_db_path)
        except Exception as e:
            print(f"Error saving index: {str(e)}")