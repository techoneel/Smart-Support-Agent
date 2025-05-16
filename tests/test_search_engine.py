import pytest
import numpy as np
from unittest.mock import Mock, patch
import faiss
from core.retriever.search_engine import SearchEngine

@pytest.fixture
def mock_index():
    """Create a mock FAISS index."""
    index = faiss.IndexFlatL2(128)  # 128-dimensional vectors
    # Add some test vectors
    vectors = np.random.randn(5, 128).astype('float32')
    index.add(vectors)
    return index

@pytest.fixture
def search_engine(temp_workspace, mock_index):
    """Create a SearchEngine instance with a mock index."""
    index_path = str(temp_workspace / "test_index")
    faiss.write_index(mock_index, index_path)
    return SearchEngine(index_path)

class TestSearchEngine:
    def test_init_with_existing_index(self, temp_workspace, mock_index):
        # Arrange
        index_path = str(temp_workspace / "test_index")
        faiss.write_index(mock_index, index_path)
        
        # Act
        engine = SearchEngine(index_path)
        
        # Assert
        assert engine.index.ntotal == mock_index.ntotal
    
    def test_search(self, search_engine):
        # Arrange
        query = "test query"
        k = 3  # Number of results to return
        
        # Act
        results = search_engine.search(query, k=k)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) <= k  # May be less if index has fewer entries
    
    @patch('numpy.random.randn')  # Mock the random embedding generation
    def test_search_with_empty_index(self, mock_randn, temp_workspace):
        # Arrange
        index_path = str(temp_workspace / "empty_index")
        empty_index = faiss.IndexFlatL2(128)
        faiss.write_index(empty_index, index_path)
        
        engine = SearchEngine(index_path)
        mock_randn.return_value = np.zeros((1, 128))
        
        # Act
        results = engine.search("test query")
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 0
    
    def test_add_document(self, search_engine):
        # Arrange
        initial_size = search_engine.index.ntotal
        document = "Test document content"
        
        # Act
        search_engine.add_document(document)
        
        # Assert
        assert search_engine.index.ntotal == initial_size + 1
    
    def test_add_documents_batch(self, search_engine):
        # Arrange
        initial_size = search_engine.index.ntotal
        documents = ["Doc 1", "Doc 2", "Doc 3"]
        
        # Act
        search_engine.add_documents(documents)
        
        # Assert
        assert search_engine.index.ntotal == initial_size + len(documents)
    
    def test_save_and_load(self, temp_workspace):
        # Arrange
        index_path = str(temp_workspace / "save_test_index")
        engine1 = SearchEngine(index_path)
        documents = ["Doc 1", "Doc 2"]
        engine1.add_documents(documents)
        size_after_add = engine1.index.ntotal
        
        # Act
        # Create new instance that should load the saved index
        engine2 = SearchEngine(index_path)
        
        # Assert
        assert engine2.index.ntotal == size_after_add
