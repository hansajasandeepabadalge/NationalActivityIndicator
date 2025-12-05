"""End-to-end classification pipeline with performance optimizations"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict
from functools import lru_cache

from sqlalchemy.orm import Session

from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.storage_service import ClassificationStorageService

logger = logging.getLogger(__name__)


class ClassificationPipeline:
    """Optimized end-to-end classification pipeline: load → classify → store"""

    def __init__(self, db: Session, batch_size: int = 50, max_workers: int = 4):
        """
        Initialize pipeline with database session and performance settings

        Args:
            db: SQLAlchemy database session
            batch_size: Number of articles to process in each batch
            max_workers: Number of concurrent workers for classification
        """
        self.loader = ArticleLoader()
        self.classifier = RuleBasedClassifier()
        self.storage = ClassificationStorageService(db)
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Performance metrics
        self.metrics = {
            'total_time': 0,
            'load_time': 0,
            'classify_time': 0,
            'store_time': 0,
            'articles_processed': 0,
            'mappings_created': 0
        }

    def run_full_pipeline(
        self,
        limit: Optional[int] = None,
        min_confidence: float = 0.3,
        use_parallel: bool = True
    ) -> dict:
        """
        Load articles, classify, and store results with optimizations

        Args:
            limit: Maximum number of articles to process (None for all)
            min_confidence: Minimum confidence threshold for storing assignments
            use_parallel: Enable parallel processing for classification

        Returns:
            Dict with processing statistics and performance metrics
        """
        start_time = time.time()
        
        try:
            # Step 1: Load and preprocess articles
            logger.info(f"Loading articles (limit={limit})...")
            load_start = time.time()
            articles = self.loader.load_and_preprocess(limit=limit)
            self.metrics['load_time'] = time.time() - load_start
            logger.info(f"✅ Loaded {len(articles)} articles in {self.metrics['load_time']:.2f}s")

            if not articles:
                logger.warning("No articles to process")
                return self._build_result(0, 0, time.time() - start_time)

            # Step 2: Classify articles (batch + parallel processing)
            logger.info(f"Classifying articles (batch_size={self.batch_size}, parallel={use_parallel})...")
            classify_start = time.time()
            
            if use_parallel and len(articles) > self.batch_size:
                total_mappings = self._classify_parallel(articles, min_confidence)
            else:
                total_mappings = self._classify_sequential(articles, min_confidence)
            
            self.metrics['classify_time'] = time.time() - classify_start
            self.metrics['articles_processed'] = len(articles)
            self.metrics['mappings_created'] = total_mappings
            self.metrics['total_time'] = time.time() - start_time

            logger.info(f"✅ Classified {len(articles)} articles in {self.metrics['classify_time']:.2f}s")
            logger.info(f"✅ Created {total_mappings} mappings")
            logger.info(f"⚡ Performance: {len(articles)/self.metrics['classify_time']:.1f} articles/sec")

            return self._build_result(len(articles), total_mappings, self.metrics['total_time'])
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

    def _classify_sequential(self, articles: List, min_confidence: float) -> int:
        """Sequential classification with batch storage"""
        total_mappings = 0
        batch_results = []
        
        for i, article in enumerate(articles, 1):
            try:
                # Classify
                assignments = self.classifier.classify_article(
                    article.cleaned_content,
                    article.title
                )
                
                # Filter by confidence
                filtered = [a for a in assignments if a['confidence'] >= min_confidence]
                
                if filtered:
                    batch_results.append({
                        'article_id': article.article_id,
                        'published_at': article.published_at,
                        'category': article.category,
                        'assignments': filtered
                    })
                
                # Store in batches
                if len(batch_results) >= self.batch_size or i == len(articles):
                    total_mappings += self._store_batch(batch_results)
                    batch_results = []
                    
            except Exception as e:
                logger.error(f"Error classifying article {article.article_id}: {e}")
                continue
        
        return total_mappings

    def _classify_parallel(self, articles: List, min_confidence: float) -> int:
        """Parallel classification with concurrent workers"""
        total_mappings = 0
        batch_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit classification tasks
            future_to_article = {
                executor.submit(self._classify_single, article, min_confidence): article
                for article in articles
            }
            
            # Collect results
            for i, future in enumerate(as_completed(future_to_article), 1):
                article = future_to_article[future]
                
                try:
                    result = future.result(timeout=30)  # 30s timeout per article
                    
                    if result:
                        batch_results.append(result)
                    
                    # Store in batches
                    if len(batch_results) >= self.batch_size or i == len(articles):
                        total_mappings += self._store_batch(batch_results)
                        batch_results = []
                        
                except Exception as e:
                    logger.error(f"Error in parallel classification for {article.article_id}: {e}")
                    continue
        
        return total_mappings

    def _classify_single(self, article, min_confidence: float) -> Optional[Dict]:
        """Classify single article (for parallel execution)"""
        try:
            assignments = self.classifier.classify_article(
                article.cleaned_content,
                article.title
            )
            
            filtered = [a for a in assignments if a['confidence'] >= min_confidence]
            
            if filtered:
                return {
                    'article_id': article.article_id,
                    'published_at': article.published_at,
                    'category': article.category,
                    'assignments': filtered
                }
        except Exception as e:
            logger.error(f"Classification error: {e}")
            
        return None

    def _store_batch(self, batch_results: List[Dict]) -> int:
        """Store batch of classification results"""
        if not batch_results:
            return 0
            
        store_start = time.time()
        total_mappings = 0
        
        try:
            for result in batch_results:
                count = self.storage.store_classifications(
                    result['article_id'],
                    result['published_at'],
                    result['category'],
                    result['assignments']
                )
                total_mappings += count
            
            store_time = time.time() - store_start
            self.metrics['store_time'] += store_time
            
        except Exception as e:
            logger.error(f"Batch storage error: {e}")
            
        return total_mappings

    def _build_result(self, articles_count: int, mappings_count: int, total_time: float) -> dict:
        """Build result dictionary with metrics"""
        return {
            'articles_processed': articles_count,
            'mappings_created': mappings_count,
            'avg_mappings_per_article': mappings_count / articles_count if articles_count > 0 else 0,
            'total_time_seconds': round(total_time, 2),
            'load_time_seconds': round(self.metrics.get('load_time', 0), 2),
            'classify_time_seconds': round(self.metrics.get('classify_time', 0), 2),
            'store_time_seconds': round(self.metrics.get('store_time', 0), 2),
            'throughput_articles_per_sec': round(articles_count / total_time, 1) if total_time > 0 else 0,
            'batch_size': self.batch_size,
            'max_workers': self.max_workers
        }

    def get_metrics(self) -> dict:
        """Get current performance metrics"""
        return self.metrics.copy()
