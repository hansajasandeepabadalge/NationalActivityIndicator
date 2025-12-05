"""Article loading and preprocessing module"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import re

from .schemas import Article, ProcessedArticle


class ArticleLoader:
    """Load and validate articles from mock data"""

    def __init__(self, mock_data_path: str = None):
        """
        Initialize article loader

        Args:
            mock_data_path: Path to mock data JSON file. If None, uses default location.
        """
        if mock_data_path is None:
            base_path = Path(__file__).parent.parent.parent.parent
            mock_data_path = base_path / "data" / "mock" / "mock_articles.json"
        self.mock_data_path = Path(mock_data_path)

    def load_articles(self, limit: Optional[int] = None) -> List[Article]:
        """
        Load articles from mock data file

        Args:
            limit: Maximum number of articles to load. If None, loads all.

        Returns:
            List of validated Article objects
        """
        with open(self.mock_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        articles_data = data.get('articles', [])
        if limit:
            articles_data = articles_data[:limit]

        validated_articles = []
        for article_data in articles_data:
            try:
                article = Article(**article_data)
                validated_articles.append(article)
            except Exception as e:
                print(f"Validation error for article {article_data.get('article_id')}: {e}")
                continue

        return validated_articles

    def preprocess_article(self, article: Article) -> ProcessedArticle:
        """
        Clean and normalize article text

        Args:
            article: Article object to preprocess

        Returns:
            ProcessedArticle with cleaned content
        """
        cleaned = self._clean_text(article.content)
        word_count = len(cleaned.split())

        return ProcessedArticle(
            **article.dict(),
            cleaned_content=cleaned,
            word_count=word_count
        )

    def _clean_text(self, text: str) -> str:
        """
        Clean article text by removing extra whitespace and special characters

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
        # Normalize unicode and strip
        text = text.strip()
        return text

    def load_and_preprocess(self, limit: Optional[int] = None) -> List[ProcessedArticle]:
        """
        Load and preprocess articles in one step

        Args:
            limit: Maximum number of articles to load

        Returns:
            List of ProcessedArticle objects
        """
        articles = self.load_articles(limit)
        return [self.preprocess_article(article) for article in articles]
