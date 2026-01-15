"""LLM service for summarizing news articles."""

import os
from typing import List, Optional
from openai import OpenAI
from anthropic import Anthropic
from google.generativeai import GenerativeModel, configure as configure_gemini

class LLMService:
    """Service for generating summaries using various LLM providers."""

    def __init__(self, provider: str = 'openai') -> None:
        self.provider = provider
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the LLM client based on provider."""
        if self.provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
        elif self.provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.client = Anthropic(api_key=api_key)
        elif self.provider == 'google':
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                configure_gemini(api_key=api_key)
                self.client = GenerativeModel('gemini-1.5-flash')
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def summarize_articles(self, articles: List[str], query: str) -> Optional[str]:
        """
        Summarize a list of article contents into a digest.

        Args:
            articles: List of article text contents.
            query: The search query/topic.

        Returns:
            Summarized digest text, or None if summarization fails.
        """
        if not self.client:
            return None

        combined_text = '\n\n'.join(articles)
        prompt = f"""
        Summarize the following news articles about "{query}" into a concise, easy-to-read digest.
        Focus on key facts, trends, and insights. Keep it under 500 words.

        Articles:
        {combined_text}
        """

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[{'role': 'user', 'content': prompt}],
                    max_tokens=500
                )
                return response.choices[0].message.content
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model='claude-3-haiku-20240307',
                    max_tokens=500,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.content[0].text
            elif self.provider == 'google':
                response = self.client.generate_content(prompt)
                return response.text
        except Exception as e:
            print(f"LLM error: {e}")
            return None

        return None