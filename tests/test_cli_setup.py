import os
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
from cli.main import setup

class TestCliSetup:
    """Tests for the CLI setup command."""
    
    @pytest.fixture
    def mock_components(self):
        """Mock all components used in the setup command."""
        with patch('cli.main.PDFParser') as mock_pdf_parser, \
             patch('cli.main.WebScraper') as mock_web_scraper, \
             patch('cli.main.IndexBuilder') as mock_index_builder, \
             patch('cli.main.Config') as mock_config:
            
            # Configure mocks
            mock_config.from_env.return_value = MagicMock(vector_db_path="data/faiss_index")
            mock_pdf_parser.return_value = MagicMock()
            mock_web_scraper.return_value = MagicMock()
            mock_index_builder.return_value = MagicMock()
            
            yield {
                'pdf_parser': mock_pdf_parser.return_value,
                'web_scraper': mock_web_scraper.return_value,
                'index_builder': mock_index_builder.return_value,
                'config': mock_config
            }
    
    def test_setup_pdf_single_file(self, mock_components):
        """Test setup with a single PDF file."""
        runner = CliRunner()
        
        # Mock PDF parser methods
        mock_components['pdf_parser'].extract_text.return_value = "Test PDF content"
        
        # Mock os.path methods
        with patch('os.path.isdir', return_value=False), \
             patch('os.path.exists', return_value=True):
            
            # Run command with simulated input
            result = runner.invoke(setup, input="y\n/path/to/document.pdf\nn\nn\n")
            
            # Verify command executed successfully
            assert result.exit_code == 0
            
            # Verify PDF parser was called correctly
            mock_components['pdf_parser'].extract_text.assert_called_once_with("/path/to/document.pdf")
            
            # Verify content was added to index
            mock_components['index_builder'].add_document.assert_called_once_with("Test PDF content")
    
    def test_setup_pdf_directory(self, mock_components):
        """Test setup with a PDF directory."""
        runner = CliRunner()
        
        # Mock PDF parser methods
        mock_documents = [
            {'file_path': '/path/docs/doc1.pdf', 'text': 'Content 1'},
            {'file_path': '/path/docs/doc2.pdf', 'text': 'Content 2'}
        ]
        mock_components['pdf_parser'].process_directory.return_value = mock_documents
        
        # Mock os.path methods
        with patch('os.path.isdir', return_value=True), \
             patch('os.path.exists', return_value=True):
            
            # Run command with simulated input
            result = runner.invoke(setup, input="y\n/path/docs\nn\nn\n")
            
            # Verify command executed successfully
            assert result.exit_code == 0
            
            # Verify PDF parser was called correctly
            mock_components['pdf_parser'].process_directory.assert_called_once_with("/path/docs")
            
            # Verify content was added to index
            assert mock_components['index_builder'].add_document.call_count == 2
            mock_components['index_builder'].add_document.assert_has_calls([
                call('Content 1'),
                call('Content 2')
            ])
    
    def test_setup_web_single_page(self, mock_components):
        """Test setup with a single web page."""
        runner = CliRunner()
        
        # Mock web scraper methods
        mock_components['web_scraper'].extract_content.return_value = {
            'content': 'Web page content',
            'metadata': {'url': 'https://example.com'}
        }
        
        # Run command with simulated input
        result = runner.invoke(setup, input="n\ny\nhttps://example.com\n1\nn\n")
        
        # Verify command executed successfully
        assert result.exit_code == 0
        
        # Verify web scraper was called correctly
        mock_components['web_scraper'].extract_content.assert_called_once_with("https://example.com")
        
        # Verify content was added to index
        mock_components['index_builder'].add_document.assert_called_once_with("Web page content")
    
    def test_setup_web_multiple_pages(self, mock_components):
        """Test setup with multiple web pages."""
        runner = CliRunner()
        
        # Mock web scraper methods
        mock_results = [
            {'content': 'Page 1 content', 'metadata': {'url': 'https://example.com/1'}},
            {'content': 'Page 2 content', 'metadata': {'url': 'https://example.com/2'}}
        ]
        mock_components['web_scraper'].crawl_site.return_value = mock_results
        
        # Run command with simulated input
        result = runner.invoke(setup, input="n\ny\nhttps://example.com\n3\nn\n")
        
        # Verify command executed successfully
        assert result.exit_code == 0
        
        # Verify web scraper was called correctly
        mock_components['web_scraper'].crawl_site.assert_called_once_with("https://example.com", max_pages=3)
        
        # Verify content was added to index
        assert mock_components['index_builder'].add_document.call_count == 2
        mock_components['index_builder'].add_document.assert_has_calls([
            call('Page 1 content'),
            call('Page 2 content')
        ])
    
    def test_setup_error_handling(self, mock_components):
        """Test error handling during setup."""
        runner = CliRunner()
        
        # Mock PDF parser to raise an exception
        mock_components['pdf_parser'].extract_text.side_effect = ValueError("Invalid PDF")
        
        # Mock os.path methods
        with patch('os.path.isdir', return_value=False), \
             patch('os.path.exists', return_value=True):
            
            # Run command with simulated input
            result = runner.invoke(setup, input="y\n/path/to/document.pdf\nn\nn\n")
            
            # Verify command executed successfully despite the error
            assert result.exit_code == 0
            
            # Verify error was handled (no exception raised)
            assert "Error processing PDF" in result.output