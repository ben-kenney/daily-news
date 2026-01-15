# Daily News Digest

A Django application that summarizes daily industry news using LLMs and sends personalized digests to users on a scheduled basis.

## Features

- User authentication with django-allauth
- Configurable LLM providers (OpenAI, Anthropic, Google Gemini)
- News search via NewsAPI with web scraping fallback
- Scheduled daily digests at 8am in user's local timezone
- Email delivery of news summaries via Sendinblue
- Web interface for managing search terms and viewing digests

## Setup

### Prerequisites

- Python 3.13+
- Redis (for Celery)
- uv package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd daily-news
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Copy environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your API keys and settings:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # API Keys
   NEWSAPI_KEY=your-newsapi-key
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   GOOGLE_API_KEY=your-google-key

   # Email settings (Sendinblue via Anymail)
   SENDINBLUE_API_KEY=your-sendinblue-api-key
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com

   # Celery
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0

   # Default LLM provider
   DEFAULT_LLM_PROVIDER=openai
   ```

5. Run migrations:
   ```bash
   cd src && uv run python manage.py migrate
   ```

6. Create superuser (optional):
   ```bash
   cd src && uv run python manage.py createsuperuser
   ```

## Usage

### Running the Application

1. Start Redis server (if not running):
   ```bash
   redis-server
   ```

2. Start Celery worker:
   ```bash
   cd src && uv run celery -A daily_news worker --loglevel=info
   ```

3. Start Celery Beat scheduler:
   ```bash
   cd src && uv run celery -A daily_news beat --loglevel=info
   ```

4. Run Django server:
   ```bash
   cd src && uv run python manage.py runserver
   ```

### User Workflow

1. Register/Login at the homepage
2. Set your timezone in Profile settings
3. Add search terms (e.g., "electric vehicle", "AI data centers")
4. View digests on the dashboard (generated daily at 8am local time)
5. Digests are also emailed automatically

### Testing

Test news search and summarization:
```bash
cd src && uv run python manage.py test_news "your search query"
```

## Architecture

- **Backend**: Django with django-allauth for authentication
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue**: Celery with Redis
- **News Search**: NewsAPI primary, web scraping fallback
- **LLM Integration**: OpenAI, Anthropic, Google Gemini
- **Email**: Sendinblue via django-anymail
- **Frontend**: Bootstrap-based templates

## API Keys Required

- **NewsAPI**: For news search (https://newsapi.org/)
- **LLM Providers**: At least one of OpenAI, Anthropic, or Google Gemini
- **Sendinblue**: API key for email delivery

## Deployment

### Production Setup

1. Set `DEBUG=False` and configure `ALLOWED_HOSTS`
2. Use PostgreSQL database
3. Configure proper email backend
4. Set up Redis and Celery in production
5. Use a WSGI server like Gunicorn
6. Set up monitoring and logging

### Environment Variables

See `.env.example` for all required environment variables.

## Development

### Code Structure

- `src/daily_news/`: Django project settings
- `src/news/`: Main app
  - `models.py`: Database models
  - `views.py`: Web views
  - `tasks.py`: Celery tasks
  - `services/`: Business logic services
  - `templates/`: HTML templates
  - `management/commands/`: Custom management commands

### Adding New Features

- Add models to `news/models.py`
- Create services in `news/services/`
- Add views in `news/views.py`
- Update URLs in `news/urls.py`
- Create templates in `news/templates/news/`

## License

[Add your license here]