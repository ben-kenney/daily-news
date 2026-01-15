from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

class UserProfile(models.Model):
    """User profile model to store additional user information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.all_timezones],
        help_text="User's preferred timezone for scheduling digests."
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"

class SearchTerm(models.Model):
    """Model for user-defined search terms for news."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    term = models.CharField(max_length=255, help_text="Search term for news, e.g., 'electric vehicle'")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'term')

    def __str__(self) -> str:
        return f"{self.user.username}: {self.term}"

class Article(models.Model):
    """Model for scraped news articles."""
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    content = models.TextField(blank=True, help_text="Scraped content of the article")
    published_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=255, blank=True)
    fetched_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title

class NewsDigest(models.Model):
    """Model for generated news digests."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_term = models.ForeignKey(SearchTerm, on_delete=models.CASCADE)
    summary = models.TextField(help_text="LLM-generated summary of the news")
    articles = models.ManyToManyField(Article, related_name='digests')
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True, help_text="When the digest was emailed")

    def __str__(self) -> str:
        return f"Digest for {self.user.username} on {self.created_at.date()}"
