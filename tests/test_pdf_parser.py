import pytest
from unittest.mock import Mock, patch
from core.ingestor.pdf_parser import PDFParser

@pytest.fixture
def mock_reader():
    """Create a mock PDF reader."""
    mock_page1 = Mock()
    mock_page1.extract_text.return_value = "Page 1 content"
    mock_page2 = Mock()
    mock_page2.extract_text.return_value = "Page 2 content"
    
    mock = Mock()
    mock.pages = [mock_page1, mock_page2]
    mock.metadata = {
        "/Title": "Test Document",
        "/Author": "Test Author",
        "/Subject": "Test Subject",
        "/Keywords": "test, pdf",
        "/Creator": "Test Creator",
        "/Producer": "Test Producer"
    }
    return mock

class TestPDFParser:
    def test_extract_text_file_not_found(self):
        parser = PDFParser()
        with pytest.raises(FileNotFoundError):
            parser.extract_text("nonexistent.pdf")
    
    def test_extract_text(self, mock_reader):
        # Arrange
        parser = PDFParser()
        
        # Act
        with patch('os.path.exists', return_value=True), \
             patch.object(parser, '_create_reader', return_value=mock_reader):
            text = parser.extract_text("test.pdf")
        
        # Assert
        assert "Page 1 content" in text
        assert "Page 2 content" in text
    
    def test_extract_metadata(self, mock_reader):
        # Arrange
        parser = PDFParser()
        
        # Act
        with patch('os.path.exists', return_value=True), \
             patch.object(parser, '_create_reader', return_value=mock_reader):
            metadata = parser.extract_metadata("test.pdf")
        
        # Assert
        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"
        assert metadata["pages"] == 2
    
    def test_process_directory_not_found(self):
        parser = PDFParser()
        with pytest.raises(NotADirectoryError):
            parser.process_directory("nonexistent_dir")
    
    def test_process_directory(self, mock_reader):
        # Arrange
        parser = PDFParser()
        
        with patch('os.path.isdir', return_value=True), \
             patch('os.walk', return_value=[("/root", [], ["doc1.pdf", "doc2.txt", "doc3.pdf"])]), \
             patch('os.path.join', side_effect=lambda *x: "/".join(x)), \
             patch('os.path.exists', return_value=True), \
             patch.object(parser, '_create_reader', return_value=mock_reader):
            
            # Act
            results = parser.process_directory("test_dir")
            
            # Assert
            assert len(results) == 2  # Only PDF files
            for doc in results:
                assert "Page 1 content" in doc["text"]
                assert doc["metadata"]["title"] == "Test Document"
                assert doc["metadata"]["pages"] == 2
