"""Celery tasks for news digest generation."""

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from .models import SearchTerm, Article, NewsDigest
from .services.news_search import NewsSearchService
from .services.article_scraper import ArticleScraper
from .services.llm_service import LLMService
import os

@shared_task
def generate_daily_digest():
    """Generate daily news digests for all users at their local 8am."""
    from .models import UserProfile
    import pytz
    from datetime import datetime

    now_utc = timezone.now()
    users = User.objects.all()
    for user in users:
        try:
            profile = user.userprofile
            user_tz = pytz.timezone(profile.timezone)
            now_user = now_utc.astimezone(user_tz)
            if now_user.hour == 8 and now_user.minute < 30:  # Run once per day around 8am
                _generate_user_digest(user)
        except UserProfile.DoesNotExist:
            # Default to UTC 8am
            if now_utc.hour == 8 and now_utc.minute < 30:
                _generate_user_digest(user)

def _generate_user_digest(user: User) -> None:
    """
    Generate digest for a specific user.

    Args:
        user: The user to generate digest for.
    """
    search_terms = SearchTerm.objects.filter(user=user)
    if not search_terms:
        return

    all_articles = []
    for term in search_terms:
        # Search for articles
        search_service = NewsSearchService()
        articles_data = search_service.search_articles(term.term)

        # Scrape content
        scraper = ArticleScraper()
        for article_data in articles_data[:5]:  # Limit to 5 per term
            url = article_data['url']
            # Check if article already exists
            article, created = Article.objects.get_or_create(
                url=url,
                defaults={
                    'title': article_data['title'],
                    'published_at': article_data.get('publishedAt'),
                    'source': article_data['source'],
                    'content': scraper.scrape_article(url) or '',
                }
            )
            if created or not article.content:
                article.content = scraper.scrape_article(url) or ''
                article.save()
            all_articles.append(article)

    if not all_articles:
        return

    # Summarize
    llm_service = LLMService(provider=os.getenv('DEFAULT_LLM_PROVIDER', 'openai'))
    contents = [a.content for a in all_articles if a.content]
    if not contents:
        return

    summary = llm_service.summarize_articles(contents, ', '.join([t.term for t in search_terms]))
    if not summary:
        return

    # Create digest
    digest = NewsDigest.objects.create(
        user=user,
        search_term=search_terms.first(),  # For simplicity, link to first term
        summary=summary,
    )
    digest.articles.set(all_articles)

    # TODO: Send email
    _send_digest_email(user, digest)

def _send_digest_email(user: User, digest: NewsDigest) -> None:
    """
    Send the digest email to the user.

    Args:
        user: The user to send to.
        digest: The digest to send.
    """
    from django.core.mail import send_mail
    subject = f"Daily News Digest for {digest.created_at.date()}"
    message = f"""
    Your daily news digest:

    {digest.summary}

    Articles:
    {chr(10).join([f"- {a.title}: {a.url}" for a in digest.articles.all()])}
    """
    send_mail(
        subject,
        message,
        os.getenv('EMAIL_HOST_USER', 'noreply@example.com'),
        [user.email],
        fail_silently=True,
    )