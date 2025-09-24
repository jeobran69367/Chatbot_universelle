"""
Web scraper module for crawling websites and extracting text content.
This module provides functionality to scrape a website and all its linked pages.
"""

import asyncio
import logging
import re
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langdetect import detect

# Import config with fallback
try:
    from config.settings import (
        MAX_PAGES_PER_SITE, REQUEST_DELAY, MAX_RETRIES, 
        TIMEOUT, SCRAPED_DATA_DIR
    )
except ImportError:
    # Fallback values if config import fails
    from pathlib import Path
    MAX_PAGES_PER_SITE = 100
    REQUEST_DELAY = 1
    MAX_RETRIES = 3
    TIMEOUT = 30
    SCRAPED_DATA_DIR = Path(__file__).parent.parent / "data" / "scraped"
    SCRAPED_DATA_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ScrapedPage:
    """Data class to store scraped page information."""
    url: str
    title: str
    content: str
    language: str
    scraped_at: datetime
    links: List[str]

class WebScraper:
    """
    Advanced web scraper that can crawl entire websites and extract text content.
    """
    
    def __init__(self, use_selenium: bool = False):
        """
        Initialize the web scraper.
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript-heavy sites
        """
        self.use_selenium = use_selenium
        self.scraped_urls: Set[str] = set()
        self.scraped_pages: List[ScrapedPage] = []
        self.session = requests.Session()
        self.driver = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup request session
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
    
    def _is_valid_url(self, url: str, base_domain: str) -> bool:
        """
        Check if URL is valid and within the same domain.
        
        Args:
            url: URL to check
            base_domain: Base domain to compare against
            
        Returns:
            True if URL is valid and within domain
        """
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
            
            # Check if it's the same domain or subdomain
            if not (parsed.netloc == base_domain or parsed.netloc.endswith(f'.{base_domain}')):
                return False
            
            # Skip non-HTML files
            skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.doc', '.docx']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
                
            return True
        except Exception:
            return False
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """
        Extract clean text content from BeautifulSoup object.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Cleaned text content
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from the page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        
        return links
    
    def _detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'fr')
        """
        try:
            if len(text) > 50:  # Only detect if text is long enough
                return detect(text)
        except Exception:
            pass
        return 'unknown'
    
    def _scrape_page_requests(self, url: str) -> Optional[ScrapedPage]:
        """
        Scrape a single page using requests library.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedPage object or None if failed
        """
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string.strip() if soup.title else url
            
            # Extract text content
            content = self._extract_text_content(soup)
            
            # Skip if content is too short
            if len(content) < 100:
                return None
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Detect language
            language = self._detect_language(content)
            
            return ScrapedPage(
                url=url,
                title=title,
                content=content,
                language=language,
                scraped_at=datetime.now(),
                links=links
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            return None
    
    def _scrape_page_selenium(self, url: str) -> Optional[ScrapedPage]:
        """
        Scrape a single page using Selenium.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedPage object or None if failed
        """
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract title
            title = self.driver.title or url
            
            # Extract text content
            content = self._extract_text_content(soup)
            
            # Skip if content is too short
            if len(content) < 100:
                return None
            
            # Extract links
            links = self._extract_links(soup, url)
            
            # Detect language
            language = self._detect_language(content)
            
            return ScrapedPage(
                url=url,
                title=title,
                content=content,
                language=language,
                scraped_at=datetime.now(),
                links=links
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url} with Selenium: {e}")
            return None
    
    def scrape_website(self, start_url: str, max_pages: Optional[int] = None) -> List[ScrapedPage]:
        """
        Scrape an entire website starting from the given URL.
        
        Args:
            start_url: Starting URL to scrape
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of scraped pages
        """
        if max_pages is None:
            max_pages = MAX_PAGES_PER_SITE
        
        # Get base domain
        base_domain = urlparse(start_url).netloc
        
        # URLs to visit
        urls_to_visit = [start_url]
        visited_urls = set()
        
        self.logger.info(f"Starting to scrape website: {start_url}")
        self.logger.info(f"Maximum pages to scrape: {max_pages}")
        
        while urls_to_visit and len(self.scraped_pages) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
            
            if not self._is_valid_url(current_url, base_domain):
                continue
            
            visited_urls.add(current_url)
            
            self.logger.info(f"Scraping page {len(self.scraped_pages) + 1}/{max_pages}: {current_url}")
            
            # Scrape the page
            if self.use_selenium and self.driver:
                scraped_page = self._scrape_page_selenium(current_url)
            else:
                scraped_page = self._scrape_page_requests(current_url)
            
            if scraped_page:
                self.scraped_pages.append(scraped_page)
                
                # Add new links to visit
                for link in scraped_page.links:
                    if link not in visited_urls and self._is_valid_url(link, base_domain):
                        urls_to_visit.append(link)
            
            # Rate limiting
            time.sleep(REQUEST_DELAY)
        
        self.logger.info(f"Scraping completed. Total pages scraped: {len(self.scraped_pages)}")
        
        # Save scraped data
        self._save_scraped_data()
        
        return self.scraped_pages
    
    def _save_scraped_data(self):
        """Save scraped data to files."""
        import json
        from pathlib import Path
        
        if not self.scraped_pages:
            return
        
        # Create filename based on first URL
        first_url = self.scraped_pages[0].url
        domain = urlparse(first_url).netloc
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.json"
        
        # Convert to JSON-serializable format
        data = []
        for page in self.scraped_pages:
            data.append({
                'url': page.url,
                'title': page.title,
                'content': page.content,
                'language': page.language,
                'scraped_at': page.scraped_at.isoformat(),
                'links': page.links
            })
        
        # Save to file
        filepath = SCRAPED_DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Scraped data saved to: {filepath}")
    
    def __del__(self):
        """Cleanup Selenium driver when object is destroyed."""
        if self.driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    scraper = WebScraper(use_selenium=False)
    pages = scraper.scrape_website("https://example.com", max_pages=10)
    
    for page in pages:
        print(f"Title: {page.title}")
        print(f"URL: {page.url}")
        print(f"Content length: {len(page.content)} characters")
        print(f"Language: {page.language}")
        print("-" * 50)
