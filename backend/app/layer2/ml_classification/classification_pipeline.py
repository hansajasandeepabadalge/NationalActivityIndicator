"""End-to-end classification pipeline"""

from sqlalchemy.orm import Session
from typing import Optional

from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.storage_service import ClassificationStorageService


class ClassificationPipeline:
    """End-to-end classification pipeline: load → classify → store"""

    def __init__(self, db: Session):
        """
        Initialize pipeline with database session

        Args:
            db: SQLAlchemy database session
        """
        self.loader = ArticleLoader()
        self.classifier = RuleBasedClassifier()
        self.storage = ClassificationStorageService(db)

    def run_full_pipeline(
        self,
        limit: Optional[int] = None,
        min_confidence: float = 0.3
    ) -> dict:
        """
        Load articles, classify, and store results

        Args:
            limit: Maximum number of articles to process (None for all)
            min_confidence: Minimum confidence threshold for storing assignments

        Returns:
            Dict with processing statistics
        """
        # Step 1: Load and preprocess articles
        print(f"Loading articles...")
        articles = self.loader.load_and_preprocess(limit=limit)
        print(f"✅ Loaded {len(articles)} articles")

        # Step 2: Classify each article
        print(f"Classifying articles...")
        total_mappings = 0

        for article in articles:
            # Get indicator assignments
            assignments = self.classifier.classify_article(
                article.cleaned_content,
                article.title
            )

            # Filter by minimum confidence
            filtered = [a for a in assignments if a['confidence'] >= min_confidence]

            # Store in database
            if filtered:
                count = self.storage.store_classifications(
                    article.article_id,
                    article.published_at,
                    article.category,
                    filtered
                )
                total_mappings += count

        print(f"✅ Classified {len(articles)} articles")
        print(f"✅ Created {total_mappings} article-indicator mappings")

        return {
            'articles_processed': len(articles),
            'mappings_created': total_mappings,
            'avg_mappings_per_article': total_mappings / len(articles) if articles else 0
        }
