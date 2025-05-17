from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urljoin, urlparse
import os
import time

class WebScraper:
    """Scraper for extracting content from web pages."""
    
    def __init__(self, user_agent: Optional[str] = None, session: Optional[Any] = None):
        """Initialize the web scraper.
        
        Args:
            user_agent (Optional[str]): Custom user agent string
            session (Optional[Any]): Custom session for testing
        """
        # Flag to track if we're using a simple session (no JS rendering)
        self.using_simple_session = False
        
        self.session = session
        if not self.session:
            try:
                # Skip HTMLSession and use simple requests directly
                self.session = requests.Session()
                self.using_simple_session = True
            except Exception as e:
                print(f"Using simple requests session: {str(e)}")
                self.session = requests.Session()
                self.using_simple_session = True
                
        # Set a user agent to avoid being blocked
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        if user_agent:
            self.session.headers['User-Agent'] = user_agent
        else:
            self.session.headers['User-Agent'] = default_ua
    
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
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Get HTML content based on session type
            if self.using_simple_session:
                # Simple requests session - no JS rendering
                html_content = response.text
            else:
                # Try to render JavaScript if possible
                try:
                    if hasattr(response, 'html') and hasattr(response.html, 'render'):
                        response.html.render(timeout=20)
                        html_content = response.html.html
                    else:
                        html_content = response.text
                except Exception as e:
                    print(f"JavaScript rendering failed, using static HTML: {str(e)}")
                    html_content = response.text
            
            # Parse content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.select('script, style, nav, footer, header'):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            # Clean and normalize text
            content = " ".join(main_content.stripped_strings) if main_content else ""
            
            # Ensure we have some content
            if not content.strip():
                print(f"Warning: No content extracted from {url}")
                # Try to get at least some text from the page
                content = " ".join(soup.stripped_strings)
                
                # If still no content, try a different approach
                if not content.strip():
                    # Try to extract all paragraph text
                    paragraphs = soup.find_all('p')
                    if paragraphs:
                        content = " ".join(p.get_text() for p in paragraphs)
                    
                    # If still no content, try to extract all div text
                    if not content.strip():
                        divs = soup.find_all('div')
                        if divs:
                            content = " ".join(d.get_text() for d in divs)
                            
                    # If still no content, use the entire HTML text
                    if not content.strip():
                        content = soup.get_text()
                        
                    # If absolutely no content, use a placeholder
                    if not content.strip():
                        content = f"No extractable content from {url}"
            
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
                
                # Be nice to the server
                time.sleep(1)
                
            except ValueError:
                # Skip failed URLs
                continue
        
        return results