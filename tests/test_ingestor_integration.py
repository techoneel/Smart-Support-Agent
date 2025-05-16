import os
import pytest
from unittest.mock import patch, MagicMock
from core.ingestor.pdf_parser import PDFParser
from core.ingestor.web_scraper import WebScraper
from core.retriever.index_builder import IndexBuilder

class TestIngestorIntegration:
    """Integration tests for the ingestor components with the index builder."""
    
    @pytest.fixture
    def setup_components(self):
        """Set up components for testing."""
        with patch('faiss.IndexFlatL2') as mock_index, \
             patch('faiss.write_index') as mock_write_index, \
             patch('faiss.read_index') as mock_read_index, \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=False):
            
            # Configure mocks
            mock_index.return_value = MagicMock()
            
            # Create components
            pdf_parser = PDFParser()
            web_scraper = WebScraper(session=MagicMock())
            
            # Create index builder with patched write_index
            with patch('core.retriever.index_builder.faiss.write_index') as patched_write:
                index_builder = IndexBuilder("data/test_index")
                
                yield {
                    'pdf_parser': pdf_parser,
                    'web_scraper': web_scraper,
                    'index_builder': index_builder,
                    'mock_index': mock_index,
                    'patched_write_index': patched_write
                }
    
    def test_pdf_to_index_integration(self, setup_components, mock_pdf_content):
        """Test PDF content being added to the index."""
        # Mock PDF parser
        setup_components['pdf_parser'].extract_text = MagicMock(return_value=mock_pdf_content)
        
        # Mock index builder's embedding method
        setup_components['index_builder']._get_embeddings = MagicMock(return_value=MagicMock())
        
        # Test the integration
        # Extract PDF content
        content = setup_components['pdf_parser'].extract_text("/fake/path.pdf")
        
        # Add to index
        setup_components['index_builder'].add_document(content)
        
        # Verify content was processed and added
        setup_components['pdf_parser'].extract_text.assert_called_once()
        setup_components['index_builder']._get_embeddings.assert_called_once()
        setup_components['patched_write_index'].assert_called()
    
    def test_web_to_index_integration(self, setup_components, mock_web_content):
        """Test web content being added to the index."""
        # Mock web scraper
        setup_components['web_scraper'].extract_content = MagicMock(return_value=mock_web_content)
        
        # Mock index builder's embedding method
        setup_components['index_builder']._get_embeddings = MagicMock(return_value=MagicMock())
        
        # Test the integration
        # Extract web content
        result = setup_components['web_scraper'].extract_content("https://example.com")
        
        # Add to index
        setup_components['index_builder'].add_document(result['content'])
        
        # Verify content was processed and added
        setup_components['web_scraper'].extract_content.assert_called_once()
        setup_components['index_builder']._get_embeddings.assert_called_once()
        setup_components['patched_write_index'].assert_called()