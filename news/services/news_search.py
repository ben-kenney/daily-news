"""News search service using NewsAPI with fallback to general web search."""

import os
import requests
from typing import List, Dict, Optional
from newsapi import NewsApiClient
from ..models import Article

class NewsSearchService:
    """Service for searching news articles."""

    def __init__(self) -> None:
        self.newsapi_key = os.getenv('NEWSAPI_KEY', '')
        self.newsapi = NewsApiClient(api_key=self.newsapi_key) if self.newsapi_key else None

    def search_articles(self, query: str, days: int = 1) -> List[Dict]:
        """
        Search for recent news articles based on query.

        Args:
            query: Search term for news.
            days: Number of days back to search.

        Returns:
            List of article dictionaries with title, url, publishedAt, source.
        """
        if self.newsapi:
            try:
                # Use NewsAPI
                response = self.newsapi.get_everything(
                    q=query,
                    language='en',
                    sort_by='publishedAt',
                    from_param=f'{days}d'
                )
                articles = []
                for item in response.get('articles', []):
                    articles.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'publishedAt': item.get('publishedAt', ''),
                        'source': item.get('source', {}).get('name', ''),
                    })
                return articles
            except Exception as e:
                print(f"NewsAPI error: {e}")
                # Fallback to general search

        # Fallback: Simple web search (placeholder, as full implementation requires API)
        # For demo, return empty or mock
        return self._fallback_search(query)

    def _fallback_search(self, query: str) -> List[Dict]:
        """
        Fallback search using general web search.

        Note: This is a placeholder. In production, use SerpAPI or similar.
        """
        # Mock response
        return [
            {
                'title': f"Sample article about {query}",
                'url': f"https://example.com/{query.replace(' ', '-')}",
                'publishedAt': '2023-01-01T00:00:00Z',
                'source': 'Example News',
            }
        ]