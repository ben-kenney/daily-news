"""Article scraping service using BeautifulSoup."""

import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urljoin

class ArticleScraper:
    """Service for scraping article content from URLs."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrape the main content of an article from the given URL.

        Args:
            url: The URL of the article to scrape.

        Returns:
            The extracted text content, or None if scraping fails.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Try to find main content
            content = self._extract_content(soup)
            return content.strip() if content else None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract main content from BeautifulSoup object.

        Args:
            soup: Parsed HTML.

        Returns:
            Extracted text content.
        """
        # Common selectors for article content
        selectors = [
            'article',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]',
            'main',
            '.entry-content',
            '#content',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=' ', strip=True)

        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            return ' '.join(p.get_text(strip=True) for p in paragraphs)

        return None