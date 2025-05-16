import pytest
from unittest.mock import Mock
from bs4 import BeautifulSoup
from core.ingestor.web_scraper import WebScraper

@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    session = Mock()
    session.headers = {}
    return session

@pytest.fixture
def web_scraper(mock_session):
    """Create a WebScraper instance with a mock session."""
    return WebScraper(session=mock_session)

class TestWebScraper:
    def test_invalid_url(self, web_scraper):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            web_scraper.extract_content("invalid-url")
        assert "Invalid URL" in str(exc_info.value)
    
    def test_extract_content(self, web_scraper, mock_session):
        # Arrange
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <main>
                    <p>Main content</p>
                    <a href="/page1">Link 1</a>
                    <a href="https://example.com/page2">Link 2</a>
                </main>
                <script>JavaScript code</script>
                <style>CSS code</style>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.html.html = html_content
        mock_session.get.return_value = mock_response
        
        # Act
        result = web_scraper.extract_content("https://example.com")
        
        # Assert
        assert "Main content" in result["content"]
        assert "JavaScript code" not in result["content"]
        assert "CSS code" not in result["content"]
        assert result["metadata"]["title"] == "Test Page"
        assert result["metadata"]["description"] == "Test description"
        assert len(result["metadata"]["links"]) == 2
    
    def test_crawl_site(self, web_scraper, mock_session):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.html.html = """
        <html>
            <head><title>Test</title></head>
            <body>
                <main>Content</main>
                <a href="https://example.com/page1">Link 1</a>
                <a href="https://example.com/page2">Link 2</a>
            </body>
        </html>
        """
        mock_session.get.return_value = mock_response
        
        # Act
        results = web_scraper.crawl_site(
            "https://example.com",
            max_pages=2,
            allowed_domains=["example.com"]
        )
        
        # Assert
        assert len(results) <= 2  # Respects max_pages
        assert all("Content" in r["content"] for r in results)
    
    def test_respect_allowed_domains(self, web_scraper, mock_session):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.html.html = """
        <html>
            <body>
                <main>Content</main>
                <a href="https://example.com/page1">Internal</a>
                <a href="https://external.com/page">External</a>
            </body>
        </html>
        """
        mock_session.get.return_value = mock_response
        
        # Act
        results = web_scraper.crawl_site(
            "https://example.com",
            max_pages=10,
            allowed_domains=["example.com"]
        )
        
        # Assert
        # Should only follow internal links
        crawled_urls = [r["metadata"]["url"] for r in results]
        assert all("example.com" in url for url in crawled_urls)
        assert not any("external.com" in url for url in crawled_urls)
    
    def test_error_handling(self, web_scraper, mock_session):
        # Arrange
        mock_session.get.side_effect = Exception("Network error")
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            web_scraper.extract_content("https://example.com")
        assert "Network error" in str(exc_info.value)
