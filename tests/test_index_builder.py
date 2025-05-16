import pytest
import os
from unittest.mock import Mock, patch
import numpy as np
import faiss
from core.retriever.index_builder import IndexBuilder

@pytest.fixture
def temp_index_path(tmp_path):
    return str(tmp_path / "test_index")

@pytest.fixture
def index_builder(temp_index_path):
    builder = IndexBuilder(temp_index_path, embedding_dim=128)
    return builder

class TestIndexBuilder:
    def test_init_creates_new_index(self, temp_index_path):
        # Act
        builder = IndexBuilder(temp_index_path, embedding_dim=128)
        
        # Assert
        assert os.path.exists(temp_index_path)
        assert isinstance(builder.index, faiss.Index)
    
    def test_add_document(self, index_builder):
        # Arrange
        content = "Test document content"
        initial_size = index_builder.index.ntotal
        
        # Act
        index_builder.add_document(content)
        
        # Assert
        assert index_builder.index.ntotal > initial_size
    
    def test_add_documents(self, index_builder):
        # Arrange
        documents = [
            "First test document",
            "Second test document",
            "Third test document"
        ]
        initial_size = index_builder.index.ntotal
        
        # Act
        index_builder.add_documents(documents)
        
        # Assert
        assert index_builder.index.ntotal > initial_size
    
    def test_index_persistence(self, temp_index_path):
        # Arrange
        builder1 = IndexBuilder(temp_index_path, embedding_dim=128)
        builder1.add_document("Test document")
        size_after_add = builder1.index.ntotal
        
        # Act
        # Create new builder instance to load the index
        builder2 = IndexBuilder(temp_index_path, embedding_dim=128)
        
        # Assert
        assert builder2.index.ntotal == size_after_add
    
    def test_embedding_dimension(self, temp_index_path):
        # Arrange
        dim = 256
        
        # Act
        builder = IndexBuilder(temp_index_path, embedding_dim=dim)
        
        # Assert
        # Get a single embedding to verify dimension
        test_embeddings = builder._get_embeddings(["test"])
        assert test_embeddings.shape[1] == dim
