"""Async batch processing utilities for Layer2 pipeline

Provides high-performance async batch processing for:
- Article ingestion
- Sentiment analysis  
- Entity extraction
- Indicator calculation
"""

import asyncio
from typing import List, Dict, Any, Callable, TypeVar, Optional, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchResult:
    """Result of a batch operation"""
    success_count: int
    error_count: int
    total_time: float
    results: List[Any]
    errors: List[Dict[str, Any]]
    throughput: float  # items per second
    
    def __repr__(self):
        return (f"BatchResult(success={self.success_count}, errors={self.error_count}, "
                f"time={self.total_time:.2f}s, throughput={self.throughput:.1f}/s)")


class AsyncBatchProcessor:
    """High-performance async batch processor
    
    Features:
    - Configurable concurrency limits
    - Automatic batching with optimal sizes
    - Error handling and retry logic
    - Progress tracking
    - Rate limiting
    """
    
    def __init__(
        self,
        max_concurrency: int = 10,
        batch_size: int = 50,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        rate_limit: Optional[float] = None  # requests per second
    ):
        self.max_concurrency = max_concurrency
        self.batch_size = batch_size
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._last_request_time = 0.0
        self._executor = ThreadPoolExecutor(max_workers=max_concurrency)
        
    async def _rate_limit_wait(self):
        """Wait to respect rate limit"""
        if self.rate_limit:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request_time = time.time()
    
    async def process_item(
        self,
        item: T,
        processor: Callable[[T], R],
        is_async: bool = False
    ) -> R:
        """Process single item with retries"""
        async with self._semaphore:
            await self._rate_limit_wait()
            
            last_error = None
            for attempt in range(self.retry_count):
                try:
                    if is_async:
                        return await processor(item)
                    else:
                        # Run sync function in executor
                        loop = asyncio.get_event_loop()
                        return await loop.run_in_executor(self._executor, processor, item)
                except Exception as e:
                    last_error = e
                    if attempt < self.retry_count - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        logger.warning(f"Retry {attempt + 1} for item due to: {e}")
            
            raise last_error
    
    async def process_batch(
        self,
        items: List[T],
        processor: Callable[[T], R],
        is_async: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """Process a batch of items concurrently
        
        Args:
            items: List of items to process
            processor: Function to process each item
            is_async: Whether processor is async
            on_progress: Optional callback(completed, total)
            
        Returns:
            BatchResult with success/error counts and results
        """
        self._semaphore = asyncio.Semaphore(self.max_concurrency)
        
        results = []
        errors = []
        completed = 0
        start_time = time.time()
        
        async def process_with_tracking(item: T, index: int):
            nonlocal completed
            try:
                result = await self.process_item(item, processor, is_async)
                completed += 1
                if on_progress:
                    on_progress(completed, len(items))
                return {"index": index, "success": True, "result": result}
            except Exception as e:
                completed += 1
                if on_progress:
                    on_progress(completed, len(items))
                return {"index": index, "success": False, "error": str(e), "item": item}
        
        # Process all items concurrently
        tasks = [
            process_with_tracking(item, i) 
            for i, item in enumerate(items)
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Separate successes and errors
        for r in all_results:
            if r["success"]:
                results.append(r["result"])
            else:
                errors.append({"index": r["index"], "error": r["error"], "item": r.get("item")})
        
        total_time = time.time() - start_time
        throughput = len(items) / total_time if total_time > 0 else 0
        
        return BatchResult(
            success_count=len(results),
            error_count=len(errors),
            total_time=total_time,
            results=results,
            errors=errors,
            throughput=throughput
        )
    
    async def process_stream(
        self,
        items: AsyncGenerator[T, None],
        processor: Callable[[T], R],
        is_async: bool = False,
        buffer_size: int = 100
    ) -> AsyncGenerator[R, None]:
        """Process items from async stream
        
        Useful for large datasets that don't fit in memory
        """
        self._semaphore = asyncio.Semaphore(self.max_concurrency)
        
        buffer = []
        async for item in items:
            buffer.append(item)
            
            if len(buffer) >= buffer_size:
                batch_result = await self.process_batch(buffer, processor, is_async)
                for result in batch_result.results:
                    yield result
                buffer = []
        
        # Process remaining items
        if buffer:
            batch_result = await self.process_batch(buffer, processor, is_async)
            for result in batch_result.results:
                yield result
    
    def close(self):
        """Clean up resources"""
        self._executor.shutdown(wait=False)


class ArticleBatchProcessor(AsyncBatchProcessor):
    """Specialized batch processor for articles"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sentiment_analyzer = None
        self._entity_extractor = None
    
    @property
    def sentiment_analyzer(self):
        if self._sentiment_analyzer is None:
            from app.layer2.nlp.sentiment_analyzer import SentimentAnalyzer
            self._sentiment_analyzer = SentimentAnalyzer(use_transformers=False)
        return self._sentiment_analyzer
    
    @property
    def entity_extractor(self):
        if self._entity_extractor is None:
            from app.layer2.nlp_processing.entity_extractor import EntityExtractor
            self._entity_extractor = EntityExtractor()
        return self._entity_extractor
    
    async def analyze_sentiments(
        self,
        articles: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """Batch analyze article sentiments"""
        
        def analyze(article: Dict) -> Dict:
            result = self.sentiment_analyzer.analyze_article(
                article_id=article.get("article_id", ""),
                title=article.get("title", ""),
                content=article.get("content", "")
            )
            return {
                "article_id": article.get("article_id"),
                "sentiment": result
            }
        
        return await self.process_batch(articles, analyze, on_progress=on_progress)
    
    async def extract_entities(
        self,
        articles: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """Batch extract entities from articles"""
        
        def extract(article: Dict) -> Dict:
            entities = self.entity_extractor.extract_entities(
                article_id=article.get("article_id", ""),
                title=article.get("title", ""),
                content=article.get("content", "")
            )
            return {
                "article_id": article.get("article_id"),
                "entities": entities
            }
        
        return await self.process_batch(articles, extract, on_progress=on_progress)
    
    async def full_pipeline(
        self,
        articles: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """Run full NLP pipeline on articles"""
        
        def process(article: Dict) -> Dict:
            # Sentiment
            sentiment = self.sentiment_analyzer.analyze_article(
                article_id=article.get("article_id", ""),
                title=article.get("title", ""),
                content=article.get("content", "")
            )
            
            # Entities
            entities = self.entity_extractor.extract_entities(
                article_id=article.get("article_id", ""),
                title=article.get("title", ""),
                content=article.get("content", "")
            )
            
            return {
                "article_id": article.get("article_id"),
                "sentiment": sentiment,
                "entities": entities,
                "processed_at": datetime.now().isoformat()
            }
        
        return await self.process_batch(articles, process, on_progress=on_progress)


class IndicatorBatchProcessor(AsyncBatchProcessor):
    """Specialized batch processor for indicator calculations"""
    
    async def calculate_indicators(
        self,
        articles_with_entities: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> BatchResult:
        """Batch calculate indicators from extracted entities"""
        from app.layer2.indicator_calculation.entity_based_calculator import EntityBasedIndicatorCalculator
        
        calculator = EntityBasedIndicatorCalculator()
        
        def calculate(item: Dict) -> Dict:
            indicators = calculator.calculate_all_indicators(item.get("entities"))
            return {
                "article_id": item.get("article_id"),
                "indicators": indicators
            }
        
        return await self.process_batch(
            articles_with_entities, 
            calculate, 
            on_progress=on_progress
        )


# Convenience functions
async def batch_analyze_articles(
    articles: List[Dict[str, Any]],
    max_concurrency: int = 10
) -> BatchResult:
    """Convenience function for batch article analysis"""
    processor = ArticleBatchProcessor(max_concurrency=max_concurrency)
    try:
        return await processor.full_pipeline(articles)
    finally:
        processor.close()


async def batch_calculate_indicators(
    articles_with_entities: List[Dict[str, Any]],
    max_concurrency: int = 10
) -> BatchResult:
    """Convenience function for batch indicator calculation"""
    processor = IndicatorBatchProcessor(max_concurrency=max_concurrency)
    try:
        return await processor.calculate_indicators(articles_with_entities)
    finally:
        processor.close()


# Global processor instance for reuse
_article_processor: Optional[ArticleBatchProcessor] = None


def get_article_processor() -> ArticleBatchProcessor:
    """Get or create global article processor"""
    global _article_processor
    if _article_processor is None:
        _article_processor = ArticleBatchProcessor(
            max_concurrency=10,
            batch_size=50,
            retry_count=3
        )
    return _article_processor
