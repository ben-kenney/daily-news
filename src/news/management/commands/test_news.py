"""Management command to test news search and summarization."""

from django.core.management.base import BaseCommand
from news.services.news_search import NewsSearchService
from news.services.article_scraper import ArticleScraper
from news.services.llm_service import LLMService
import os

class Command(BaseCommand):
    """Test news search and summarization."""

    help = 'Test news search and summarization functionality'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='Search query for news')

    def handle(self, *args, **options):
        query = options['query']
        self.stdout.write(f'Testing news search for: {query}')

        # Test search
        search_service = NewsSearchService()
        articles = search_service.search_articles(query)
        self.stdout.write(f'Found {len(articles)} articles')

        if not articles:
            return

        # Test scraping
        scraper = ArticleScraper()
        contents = []
        for article in articles[:3]:  # Test with first 3
            content = scraper.scrape_article(article['url'])
            if content:
                contents.append(content[:500])  # Limit for testing
                self.stdout.write(f'Scraped: {article["title"]}')

        if not contents:
            self.stdout.write('No content scraped')
            return

        # Test summarization
        llm_service = LLMService(provider=os.getenv('DEFAULT_LLM_PROVIDER', 'openai'))
        summary = llm_service.summarize_articles(contents, query)
        if summary:
            self.stdout.write('Summary:')
            self.stdout.write(summary)
        else:
            self.stdout.write('Summarization failed')