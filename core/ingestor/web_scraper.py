from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin, urlparse

class WebScraper:
    """Scraper for extracting content from web pages."""
    
    def __init__(self, user_agent: Optional[str] = None, session: Optional[Any] = None):
        """Initialize the web scraper.
        
        Args:
            user_agent (Optional[str]): Custom user agent string
            session (Optional[Any]): Custom session for testing
        """
        from requests_html import HTMLSession
        self.session = session or HTMLSession()
        if user_agent:
            self.session.headers['User-Agent'] = user_agent
    
    def extract_content(self, url: str) -> Dict[str, Any]:
        """Extract content from a web page.
        
        Args:
            url (str): URL of the web page
            
        Returns:
            Dict[str, Any]: Extracted content and metadata
            
        Raises:
            ValueError: If the URL is invalid or unreachable
        """
        try:
            # Validate URL
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError(f"Invalid URL: {url}")
            
            # Fetch page
            response = self.session.get(url)
            response.raise_for_status()
            
            # Render JavaScript if needed
            response.html.render(timeout=20)
            
            # Parse content
            soup = BeautifulSoup(response.html.html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.select('script, style, nav, footer, header'):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            # Clean and normalize text
            content = " ".join(main_content.stripped_strings) if main_content else ""
            
            # Extract metadata
            metadata = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "description": (
                    soup.find('meta', attrs={'name': 'description'})
                    .get('content', '') if soup.find('meta', attrs={'name': 'description'})
                    else ""
                ),
                "links": [
                    urljoin(url, a.get('href'))
                    for a in soup.find_all('a', href=True)
                ]
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except Exception as e:
            raise ValueError(f"Failed to scrape {url}: {str(e)}")
    
    def crawl_site(
        self,
        start_url: str,
        max_pages: int = 10,
        allowed_domains: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Crawl a website starting from a URL.
        
        Args:
            start_url (str): Starting URL
            max_pages (int): Maximum number of pages to crawl
            allowed_domains (Optional[List[str]]): List of allowed domains
            
        Returns:
            List[Dict[str, Any]]: List of extracted content and metadata
        """
        crawled_urls = set()
        to_crawl = [start_url]
        results = []
        
        # Set up domain restrictions
        if allowed_domains is None:
            allowed_domains = [urlparse(start_url).netloc]
        
        while to_crawl and len(results) < max_pages:
            current_url = to_crawl.pop(0)
            
            # Skip if already crawled
            if current_url in crawled_urls:
                continue
                
            # Check if domain is allowed
            current_domain = urlparse(current_url).netloc
            if current_domain not in allowed_domains:
                continue
            
            try:
                # Extract content from current page
                page_data = self.extract_content(current_url)
                results.append(page_data)
                crawled_urls.add(current_url)
                
                # Add new URLs to crawl queue
                new_urls = [
                    url for url in page_data["metadata"]["links"]
                    if url not in crawled_urls
                    and urlparse(url).netloc in allowed_domains
                ]
                to_crawl.extend(new_urls)
                
            except ValueError:
                # Skip failed URLs
                continue
        
        return results
