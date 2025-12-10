"""
Performance Optimizer for Layer 1 Adaptive Learning System.

Optimizes scraper performance, retry strategies, request patterns,
and resource utilization based on learned patterns.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of performance optimizations."""
    RETRY_STRATEGY = "retry_strategy"
    REQUEST_TIMING = "request_timing"
    CONCURRENCY = "concurrency"
    TIMEOUT = "timeout"
    CACHE_POLICY = "cache_policy"
    BATCH_SIZE = "batch_size"
    RESOURCE_ALLOCATION = "resource_allocation"


@dataclass
class PerformanceProfile:
    """Performance profile for a source or scraper."""
    entity_id: str
    entity_type: str  # "source" or "scraper"
    
    # Timing metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Success metrics
    success_rate: float = 1.0
    retry_success_rate: float = 0.0  # Success rate of retried requests
    
    # Failure patterns
    timeout_rate: float = 0.0
    rate_limit_rate: float = 0.0
    server_error_rate: float = 0.0
    
    # Optimal settings (learned)
    optimal_timeout_ms: int = 30000
    optimal_retry_count: int = 3
    optimal_retry_delay_ms: int = 1000
    optimal_concurrency: int = 5
    optimal_batch_size: int = 10
    
    # Time patterns
    peak_hours: List[int] = field(default_factory=list)  # 0-23
    best_hours: List[int] = field(default_factory=list)  # Hours with best success
    
    # History
    last_updated: Optional[datetime] = None
    sample_count: int = 0


@dataclass
class OptimizationRecommendation:
    """A recommendation for performance optimization."""
    optimization_type: OptimizationType
    entity_id: str
    current_value: Any
    recommended_value: Any
    expected_improvement: float  # Percentage improvement expected
    confidence: float  # 0.0 to 1.0
    reasoning: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequestPattern:
    """Tracks request patterns for optimization."""
    hour: int  # 0-23
    day_of_week: int  # 0-6 (Monday-Sunday)
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    request_count: int = 0


@dataclass
class RetryStrategy:
    """Optimized retry strategy configuration."""
    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    exponential_base: float = 2.0
    jitter_factor: float = 0.1  # Add randomness to prevent thundering herd
    
    # Conditional retries
    retry_on_timeout: bool = True
    retry_on_rate_limit: bool = True
    retry_on_server_error: bool = True
    retry_on_connection_error: bool = True
    
    # Rate limit specific
    rate_limit_backoff_ms: int = 60000  # Wait 1 min on rate limit


class PerformanceOptimizer:
    """
    Optimizes Layer 1 performance based on learned patterns.
    
    Features:
    - Learns optimal retry strategies per source
    - Discovers best request timing patterns
    - Optimizes concurrency and resource allocation
    - Provides intelligent recommendations
    """
    
    def __init__(
        self,
        db_pool=None,
        min_samples_for_optimization: int = 100,
        optimization_interval_hours: int = 6
    ):
        self.db_pool = db_pool
        self.min_samples = min_samples_for_optimization
        self.optimization_interval = timedelta(hours=optimization_interval_hours)
        
        # In-memory caches
        self._profiles: Dict[str, PerformanceProfile] = {}
        self._patterns: Dict[str, List[RequestPattern]] = {}  # entity_id -> patterns
        self._retry_strategies: Dict[str, RetryStrategy] = {}
        self._recommendations: List[OptimizationRecommendation] = []
        
        # Default configurations
        self._default_retry = RetryStrategy()
        self._last_optimization: Optional[datetime] = None
        
        # Performance thresholds
        self.GOOD_SUCCESS_RATE = 0.95
        self.ACCEPTABLE_SUCCESS_RATE = 0.85
        self.GOOD_LATENCY_MS = 2000
        self.ACCEPTABLE_LATENCY_MS = 5000
    
    async def record_request(
        self,
        entity_id: str,
        entity_type: str,
        success: bool,
        latency_ms: float,
        retry_count: int = 0,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record a request result for learning.
        
        Args:
            entity_id: Source or scraper identifier
            entity_type: "source" or "scraper"
            success: Whether request succeeded
            latency_ms: Request latency in milliseconds
            retry_count: Number of retries performed
            error_type: Type of error if failed (timeout, rate_limit, server_error, etc.)
        """
        # Get or create profile
        profile = self._get_or_create_profile(entity_id, entity_type)
        
        # Update timing metrics
        profile.sample_count += 1
        n = profile.sample_count
        
        # Running average for response time
        profile.avg_response_time_ms = (
            (profile.avg_response_time_ms * (n - 1) + latency_ms) / n
        )
        
        # Track p95/p99 (simplified - in production use reservoir sampling)
        if latency_ms > profile.p95_response_time_ms:
            profile.p95_response_time_ms = (
                profile.p95_response_time_ms * 0.95 + latency_ms * 0.05
            )
        if latency_ms > profile.p99_response_time_ms:
            profile.p99_response_time_ms = (
                profile.p99_response_time_ms * 0.99 + latency_ms * 0.01
            )
        
        # Update success rate
        if success:
            profile.success_rate = (
                (profile.success_rate * (n - 1) + 1) / n
            )
            if retry_count > 0:
                # Track retry success separately
                profile.retry_success_rate = (
                    profile.retry_success_rate * 0.9 + 0.1
                )
        else:
            profile.success_rate = (
                (profile.success_rate * (n - 1)) / n
            )
            
            # Track error types
            if error_type == "timeout":
                profile.timeout_rate = profile.timeout_rate * 0.95 + 0.05
            elif error_type == "rate_limit":
                profile.rate_limit_rate = profile.rate_limit_rate * 0.95 + 0.05
            elif error_type == "server_error":
                profile.server_error_rate = profile.server_error_rate * 0.95 + 0.05
        
        profile.last_updated = datetime.now()
        
        # Record time pattern
        await self._record_time_pattern(entity_id, success, latency_ms)
        
        # Persist to database periodically
        if profile.sample_count % 100 == 0:
            await self._persist_profile(profile)
        
        logger.debug(
            f"Recorded request for {entity_type}/{entity_id}: "
            f"success={success}, latency={latency_ms:.0f}ms"
        )
    
    async def _record_time_pattern(
        self,
        entity_id: str,
        success: bool,
        latency_ms: float
    ) -> None:
        """Record time-based patterns for optimization."""
        now = datetime.now()
        hour = now.hour
        day = now.weekday()
        
        if entity_id not in self._patterns:
            # Initialize patterns for all hour/day combinations
            self._patterns[entity_id] = [
                RequestPattern(hour=h, day_of_week=d)
                for h in range(24)
                for d in range(7)
            ]
        
        # Find matching pattern
        for pattern in self._patterns[entity_id]:
            if pattern.hour == hour and pattern.day_of_week == day:
                pattern.request_count += 1
                pattern.total_latency_ms += latency_ms
                pattern.avg_latency_ms = (
                    pattern.total_latency_ms / pattern.request_count
                )
                if success:
                    pattern.success_count += 1
                else:
                    pattern.failure_count += 1
                break
    
    def _get_or_create_profile(
        self,
        entity_id: str,
        entity_type: str
    ) -> PerformanceProfile:
        """Get or create a performance profile."""
        if entity_id not in self._profiles:
            self._profiles[entity_id] = PerformanceProfile(
                entity_id=entity_id,
                entity_type=entity_type
            )
        return self._profiles[entity_id]
    
    async def get_retry_strategy(self, entity_id: str) -> RetryStrategy:
        """
        Get optimized retry strategy for an entity.
        
        Returns learned optimal settings or defaults.
        """
        if entity_id in self._retry_strategies:
            return self._retry_strategies[entity_id]
        
        # Check if we have enough data to optimize
        profile = self._profiles.get(entity_id)
        if profile and profile.sample_count >= self.min_samples:
            strategy = await self._compute_optimal_retry_strategy(profile)
            self._retry_strategies[entity_id] = strategy
            return strategy
        
        return self._default_retry
    
    async def _compute_optimal_retry_strategy(
        self,
        profile: PerformanceProfile
    ) -> RetryStrategy:
        """Compute optimal retry strategy based on profile."""
        strategy = RetryStrategy()
        
        # Adjust retries based on retry success rate
        if profile.retry_success_rate > 0.5:
            # Retries are effective, allow more
            strategy.max_retries = min(5, strategy.max_retries + 1)
        elif profile.retry_success_rate < 0.2:
            # Retries rarely help, reduce
            strategy.max_retries = max(1, strategy.max_retries - 1)
        
        # Adjust timeout based on p95 latency
        if profile.p95_response_time_ms > 0:
            # Set timeout to 1.5x p95 latency, with bounds
            optimal_timeout = int(profile.p95_response_time_ms * 1.5)
            strategy.base_delay_ms = max(500, min(60000, optimal_timeout))
        
        # Adjust rate limit backoff if we're hitting limits
        if profile.rate_limit_rate > 0.1:
            # Increase backoff
            strategy.rate_limit_backoff_ms = min(
                120000,  # Max 2 min
                int(strategy.rate_limit_backoff_ms * 1.5)
            )
        
        # Adjust exponential base based on server error patterns
        if profile.server_error_rate > 0.1:
            # More aggressive backoff for server errors
            strategy.exponential_base = 2.5
        
        logger.info(
            f"Computed retry strategy for {profile.entity_id}: "
            f"retries={strategy.max_retries}, delay={strategy.base_delay_ms}ms"
        )
        
        return strategy
    
    async def get_optimal_timing(
        self,
        entity_id: str
    ) -> Dict[str, Any]:
        """
        Get optimal timing recommendations for an entity.
        
        Returns best hours, worst hours, and recommended scheduling.
        """
        patterns = self._patterns.get(entity_id, [])
        
        if not patterns or sum(p.request_count for p in patterns) < self.min_samples:
            return {
                "has_data": False,
                "best_hours": list(range(6, 22)),  # Default: business hours
                "worst_hours": [],
                "recommendation": "Insufficient data for timing optimization"
            }
        
        # Analyze by hour (aggregate across days)
        hour_stats: Dict[int, Dict[str, float]] = {}
        
        for pattern in patterns:
            if pattern.hour not in hour_stats:
                hour_stats[pattern.hour] = {
                    "success_count": 0,
                    "failure_count": 0,
                    "total_latency": 0,
                    "request_count": 0
                }
            
            hour_stats[pattern.hour]["success_count"] += pattern.success_count
            hour_stats[pattern.hour]["failure_count"] += pattern.failure_count
            hour_stats[pattern.hour]["total_latency"] += pattern.total_latency_ms
            hour_stats[pattern.hour]["request_count"] += pattern.request_count
        
        # Calculate success rates per hour
        hour_performance: List[Tuple[int, float, float]] = []  # (hour, success_rate, avg_latency)
        
        for hour, stats in hour_stats.items():
            total = stats["success_count"] + stats["failure_count"]
            if total > 0:
                success_rate = stats["success_count"] / total
                avg_latency = (
                    stats["total_latency"] / stats["request_count"]
                    if stats["request_count"] > 0 else 0
                )
                hour_performance.append((hour, success_rate, avg_latency))
        
        # Sort by success rate, then by latency
        hour_performance.sort(key=lambda x: (-x[1], x[2]))
        
        best_hours = [h for h, sr, _ in hour_performance[:6] if sr >= self.ACCEPTABLE_SUCCESS_RATE]
        worst_hours = [h for h, sr, _ in hour_performance if sr < self.ACCEPTABLE_SUCCESS_RATE]
        
        return {
            "has_data": True,
            "best_hours": best_hours or list(range(24)),
            "worst_hours": worst_hours,
            "hour_details": {
                h: {"success_rate": sr, "avg_latency_ms": lat}
                for h, sr, lat in hour_performance
            },
            "recommendation": self._generate_timing_recommendation(best_hours, worst_hours)
        }
    
    def _generate_timing_recommendation(
        self,
        best_hours: List[int],
        worst_hours: List[int]
    ) -> str:
        """Generate human-readable timing recommendation."""
        if not worst_hours:
            return "Source performs consistently well at all hours"
        
        if len(best_hours) < 3:
            return f"Consider scheduling requests during hours: {best_hours}"
        
        if worst_hours:
            return f"Avoid hours {worst_hours} when possible; best performance at {best_hours[:3]}"
        
        return "No specific timing recommendations"
    
    async def get_optimal_concurrency(self, entity_id: str) -> int:
        """Get optimal concurrency level for an entity."""
        profile = self._profiles.get(entity_id)
        
        if not profile or profile.sample_count < self.min_samples:
            return 5  # Default concurrency
        
        # Base concurrency on success rate and latency
        base_concurrency = 5
        
        # High success rate and low latency = can increase concurrency
        if (profile.success_rate > self.GOOD_SUCCESS_RATE and 
            profile.avg_response_time_ms < self.GOOD_LATENCY_MS):
            base_concurrency = 10
        
        # Low success rate = reduce concurrency
        elif profile.success_rate < self.ACCEPTABLE_SUCCESS_RATE:
            base_concurrency = 3
        
        # High rate limit rate = significantly reduce
        if profile.rate_limit_rate > 0.1:
            base_concurrency = max(1, base_concurrency // 2)
        
        profile.optimal_concurrency = base_concurrency
        return base_concurrency
    
    async def analyze_and_optimize(self) -> List[OptimizationRecommendation]:
        """
        Run full optimization analysis and generate recommendations.
        
        Returns list of optimization recommendations.
        """
        now = datetime.now()
        
        # Rate limit optimization runs
        if (self._last_optimization and 
            now - self._last_optimization < self.optimization_interval):
            return self._recommendations
        
        self._last_optimization = now
        recommendations: List[OptimizationRecommendation] = []
        
        for entity_id, profile in self._profiles.items():
            if profile.sample_count < self.min_samples:
                continue
            
            # Analyze timeout optimization
            timeout_rec = await self._analyze_timeout(profile)
            if timeout_rec:
                recommendations.append(timeout_rec)
            
            # Analyze retry optimization
            retry_rec = await self._analyze_retry(profile)
            if retry_rec:
                recommendations.append(retry_rec)
            
            # Analyze concurrency optimization
            concurrency_rec = await self._analyze_concurrency(profile)
            if concurrency_rec:
                recommendations.append(concurrency_rec)
            
            # Analyze batch size optimization
            batch_rec = await self._analyze_batch_size(profile)
            if batch_rec:
                recommendations.append(batch_rec)
        
        self._recommendations = recommendations
        
        logger.info(f"Generated {len(recommendations)} optimization recommendations")
        
        return recommendations
    
    async def _analyze_timeout(
        self,
        profile: PerformanceProfile
    ) -> Optional[OptimizationRecommendation]:
        """Analyze and recommend timeout adjustments."""
        if profile.timeout_rate < 0.01:
            return None  # No timeout issues
        
        # If high timeout rate, suggest increasing timeout
        if profile.timeout_rate > 0.05:
            current_timeout = profile.optimal_timeout_ms
            recommended = int(profile.p99_response_time_ms * 1.5)
            recommended = max(recommended, current_timeout * 1.2)
            
            return OptimizationRecommendation(
                optimization_type=OptimizationType.TIMEOUT,
                entity_id=profile.entity_id,
                current_value=current_timeout,
                recommended_value=min(60000, int(recommended)),
                expected_improvement=profile.timeout_rate * 0.5,  # Expect 50% reduction in timeouts
                confidence=min(0.9, profile.sample_count / 500),
                reasoning=f"Timeout rate of {profile.timeout_rate:.1%} detected. "
                         f"P99 latency is {profile.p99_response_time_ms:.0f}ms."
            )
        
        return None
    
    async def _analyze_retry(
        self,
        profile: PerformanceProfile
    ) -> Optional[OptimizationRecommendation]:
        """Analyze and recommend retry strategy adjustments."""
        current_retries = profile.optimal_retry_count
        
        # High retry success rate = retries are valuable
        if profile.retry_success_rate > 0.5 and current_retries < 5:
            return OptimizationRecommendation(
                optimization_type=OptimizationType.RETRY_STRATEGY,
                entity_id=profile.entity_id,
                current_value=current_retries,
                recommended_value=min(5, current_retries + 1),
                expected_improvement=profile.retry_success_rate * 0.1,
                confidence=min(0.85, profile.sample_count / 500),
                reasoning=f"Retry success rate of {profile.retry_success_rate:.1%} suggests "
                         f"retries are effective. Increasing max retries."
            )
        
        # Very low retry success rate = reduce retries to save resources
        if profile.retry_success_rate < 0.1 and current_retries > 1:
            return OptimizationRecommendation(
                optimization_type=OptimizationType.RETRY_STRATEGY,
                entity_id=profile.entity_id,
                current_value=current_retries,
                recommended_value=max(1, current_retries - 1),
                expected_improvement=0.05,  # Resource savings
                confidence=min(0.8, profile.sample_count / 500),
                reasoning=f"Retry success rate of {profile.retry_success_rate:.1%} is low. "
                         f"Reducing retries to conserve resources."
            )
        
        return None
    
    async def _analyze_concurrency(
        self,
        profile: PerformanceProfile
    ) -> Optional[OptimizationRecommendation]:
        """Analyze and recommend concurrency adjustments."""
        current = profile.optimal_concurrency
        
        # Rate limiting = reduce concurrency
        if profile.rate_limit_rate > 0.05:
            new_concurrency = max(1, current // 2)
            if new_concurrency != current:
                return OptimizationRecommendation(
                    optimization_type=OptimizationType.CONCURRENCY,
                    entity_id=profile.entity_id,
                    current_value=current,
                    recommended_value=new_concurrency,
                    expected_improvement=profile.rate_limit_rate * 0.7,
                    confidence=min(0.9, profile.sample_count / 300),
                    reasoning=f"Rate limiting detected ({profile.rate_limit_rate:.1%}). "
                             f"Reducing concurrency to avoid throttling."
                )
        
        # High success rate + low latency = can increase
        if (profile.success_rate > self.GOOD_SUCCESS_RATE and
            profile.avg_response_time_ms < self.GOOD_LATENCY_MS and
            profile.rate_limit_rate < 0.01 and
            current < 15):
            new_concurrency = min(15, current + 2)
            return OptimizationRecommendation(
                optimization_type=OptimizationType.CONCURRENCY,
                entity_id=profile.entity_id,
                current_value=current,
                recommended_value=new_concurrency,
                expected_improvement=0.1,  # 10% throughput improvement
                confidence=min(0.75, profile.sample_count / 500),
                reasoning=f"Excellent performance metrics (success: {profile.success_rate:.1%}, "
                         f"latency: {profile.avg_response_time_ms:.0f}ms). "
                         f"Can safely increase concurrency."
            )
        
        return None
    
    async def _analyze_batch_size(
        self,
        profile: PerformanceProfile
    ) -> Optional[OptimizationRecommendation]:
        """Analyze and recommend batch size adjustments."""
        current = profile.optimal_batch_size
        
        # If server errors are high, reduce batch size
        if profile.server_error_rate > 0.05:
            new_size = max(5, current - 5)
            if new_size != current:
                return OptimizationRecommendation(
                    optimization_type=OptimizationType.BATCH_SIZE,
                    entity_id=profile.entity_id,
                    current_value=current,
                    recommended_value=new_size,
                    expected_improvement=profile.server_error_rate * 0.3,
                    confidence=min(0.7, profile.sample_count / 300),
                    reasoning=f"Server error rate of {profile.server_error_rate:.1%}. "
                             f"Reducing batch size to decrease server load."
                )
        
        return None
    
    async def apply_recommendation(
        self,
        recommendation: OptimizationRecommendation,
        dry_run: bool = True
    ) -> bool:
        """
        Apply an optimization recommendation.
        
        Args:
            recommendation: The recommendation to apply
            dry_run: If True, only log what would be done
            
        Returns:
            True if applied/would apply successfully
        """
        entity_id = recommendation.entity_id
        opt_type = recommendation.optimization_type
        
        if dry_run:
            logger.info(
                f"[DRY RUN] Would apply {opt_type.value} optimization for {entity_id}: "
                f"{recommendation.current_value} -> {recommendation.recommended_value}"
            )
            return True
        
        profile = self._profiles.get(entity_id)
        if not profile:
            logger.warning(f"Profile not found for {entity_id}")
            return False
        
        # Apply based on type
        if opt_type == OptimizationType.TIMEOUT:
            profile.optimal_timeout_ms = recommendation.recommended_value
        elif opt_type == OptimizationType.RETRY_STRATEGY:
            profile.optimal_retry_count = recommendation.recommended_value
            if entity_id in self._retry_strategies:
                self._retry_strategies[entity_id].max_retries = recommendation.recommended_value
        elif opt_type == OptimizationType.CONCURRENCY:
            profile.optimal_concurrency = recommendation.recommended_value
        elif opt_type == OptimizationType.BATCH_SIZE:
            profile.optimal_batch_size = recommendation.recommended_value
        
        logger.info(
            f"Applied {opt_type.value} optimization for {entity_id}: "
            f"{recommendation.current_value} -> {recommendation.recommended_value}"
        )
        
        # Persist changes
        await self._persist_profile(profile)
        
        return True
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance across all tracked entities."""
        if not self._profiles:
            return {
                "total_entities": 0,
                "message": "No performance data collected yet"
            }
        
        profiles = list(self._profiles.values())
        
        success_rates = [p.success_rate for p in profiles if p.sample_count > 0]
        latencies = [p.avg_response_time_ms for p in profiles if p.sample_count > 0]
        
        healthy = sum(1 for p in profiles if p.success_rate >= self.GOOD_SUCCESS_RATE)
        degraded = sum(
            1 for p in profiles 
            if self.ACCEPTABLE_SUCCESS_RATE <= p.success_rate < self.GOOD_SUCCESS_RATE
        )
        unhealthy = sum(1 for p in profiles if p.success_rate < self.ACCEPTABLE_SUCCESS_RATE)
        
        return {
            "total_entities": len(profiles),
            "total_samples": sum(p.sample_count for p in profiles),
            "health": {
                "healthy": healthy,
                "degraded": degraded,
                "unhealthy": unhealthy
            },
            "success_rate": {
                "average": statistics.mean(success_rates) if success_rates else 0,
                "min": min(success_rates) if success_rates else 0,
                "max": max(success_rates) if success_rates else 0
            },
            "latency_ms": {
                "average": statistics.mean(latencies) if latencies else 0,
                "min": min(latencies) if latencies else 0,
                "max": max(latencies) if latencies else 0
            },
            "pending_recommendations": len(self._recommendations),
            "last_optimization": (
                self._last_optimization.isoformat() 
                if self._last_optimization else None
            )
        }
    
    async def _persist_profile(self, profile: PerformanceProfile) -> None:
        """Persist profile to database."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO l1_performance_profiles (
                        entity_id, entity_type, avg_response_time_ms,
                        p95_response_time_ms, p99_response_time_ms,
                        success_rate, retry_success_rate,
                        timeout_rate, rate_limit_rate, server_error_rate,
                        optimal_timeout_ms, optimal_retry_count,
                        optimal_concurrency, optimal_batch_size,
                        sample_count, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW())
                    ON CONFLICT (entity_id) DO UPDATE SET
                        avg_response_time_ms = $3,
                        p95_response_time_ms = $4,
                        p99_response_time_ms = $5,
                        success_rate = $6,
                        retry_success_rate = $7,
                        timeout_rate = $8,
                        rate_limit_rate = $9,
                        server_error_rate = $10,
                        optimal_timeout_ms = $11,
                        optimal_retry_count = $12,
                        optimal_concurrency = $13,
                        optimal_batch_size = $14,
                        sample_count = $15,
                        updated_at = NOW()
                """,
                    profile.entity_id, profile.entity_type,
                    profile.avg_response_time_ms, profile.p95_response_time_ms,
                    profile.p99_response_time_ms, profile.success_rate,
                    profile.retry_success_rate, profile.timeout_rate,
                    profile.rate_limit_rate, profile.server_error_rate,
                    profile.optimal_timeout_ms, profile.optimal_retry_count,
                    profile.optimal_concurrency, profile.optimal_batch_size,
                    profile.sample_count
                )
        except Exception as e:
            logger.error(f"Failed to persist profile: {e}")
    
    async def load_profiles(self) -> None:
        """Load profiles from database."""
        if not self.db_pool:
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM l1_performance_profiles
                """)
                
                for row in rows:
                    profile = PerformanceProfile(
                        entity_id=row["entity_id"],
                        entity_type=row["entity_type"],
                        avg_response_time_ms=row["avg_response_time_ms"],
                        p95_response_time_ms=row["p95_response_time_ms"],
                        p99_response_time_ms=row["p99_response_time_ms"],
                        success_rate=row["success_rate"],
                        retry_success_rate=row["retry_success_rate"],
                        timeout_rate=row["timeout_rate"],
                        rate_limit_rate=row["rate_limit_rate"],
                        server_error_rate=row["server_error_rate"],
                        optimal_timeout_ms=row["optimal_timeout_ms"],
                        optimal_retry_count=row["optimal_retry_count"],
                        optimal_concurrency=row["optimal_concurrency"],
                        optimal_batch_size=row["optimal_batch_size"],
                        sample_count=row["sample_count"],
                        last_updated=row["updated_at"]
                    )
                    self._profiles[profile.entity_id] = profile
                
                logger.info(f"Loaded {len(rows)} performance profiles")
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
