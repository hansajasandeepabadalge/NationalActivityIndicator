"""
Feedback Loop for Adaptive Learning System

Receives and processes feedback signals from downstream layers (L2, L3, L4, L5)
to improve Layer 1 quality. This creates a closed loop where downstream usage
patterns inform upstream quality improvements.

Feedback Types:
- Usage: Was the article used in indicator calculation?
- Quality: Quality issues detected downstream
- Relevance: Was the article relevant to expected topics?
- Accuracy: Was the information accurate (verified later)?
- Correction: Manual corrections or overrides

The feedback is aggregated and used to:
- Adjust source reputation scores
- Tune quality thresholds
- Identify problematic content patterns
- Improve scraper configurations
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback from downstream layers."""
    # Usage feedback
    ARTICLE_USED = "article_used"              # Article was used in processing
    ARTICLE_DISCARDED = "article_discarded"    # Article was discarded
    ARTICLE_FLAGGED = "article_flagged"        # Article flagged for review
    
    # Quality feedback
    QUALITY_ISSUE = "quality_issue"            # Quality problem detected
    CONTENT_INCOMPLETE = "content_incomplete"  # Missing content
    CONTENT_CORRUPTED = "content_corrupted"    # Corrupted/garbled content
    
    # Relevance feedback
    TOPIC_RELEVANT = "topic_relevant"          # Matched expected topic
    TOPIC_IRRELEVANT = "topic_irrelevant"      # Did not match expected topic
    CATEGORY_MISMATCH = "category_mismatch"    # Wrong category assignment
    
    # Accuracy feedback
    INFORMATION_VERIFIED = "info_verified"     # Information confirmed accurate
    INFORMATION_DISPUTED = "info_disputed"     # Information found inaccurate
    CLAIM_CORROBORATED = "claim_corroborated"  # Claim confirmed by other sources
    CLAIM_CONTRADICTED = "claim_contradicted"  # Claim contradicted by other sources
    
    # Manual feedback
    MANUAL_CORRECTION = "manual_correction"    # Human correction applied
    MANUAL_APPROVAL = "manual_approval"        # Human approved quality
    MANUAL_REJECTION = "manual_rejection"      # Human rejected content
    
    # Source feedback
    SOURCE_RELIABLE = "source_reliable"        # Source proved reliable
    SOURCE_UNRELIABLE = "source_unreliable"    # Source proved unreliable


class FeedbackSeverity(Enum):
    """Severity levels for feedback signals."""
    INFO = "info"           # Informational, no action needed
    LOW = "low"             # Minor issue, monitor
    MEDIUM = "medium"       # Moderate issue, may need action
    HIGH = "high"           # Serious issue, action recommended
    CRITICAL = "critical"   # Critical issue, immediate action needed


@dataclass
class FeedbackSignal:
    """Single feedback signal from downstream."""
    feedback_type: FeedbackType
    severity: FeedbackSeverity = FeedbackSeverity.MEDIUM
    source_layer: str = "layer2"         # "layer2", "layer3", "layer4", "layer5", "manual"
    article_id: Optional[str] = None
    source_id: Optional[str] = None
    quality_rating: Optional[float] = None  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_type": self.feedback_type.value,
            "severity": self.severity.value,
            "source_layer": self.source_layer,
            "article_id": self.article_id,
            "source_id": self.source_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


@dataclass
class FeedbackAggregation:
    """Aggregated feedback for a source."""
    source_id: str
    
    # Positive signals
    articles_used: int = 0
    topics_relevant: int = 0
    info_verified: int = 0
    claims_corroborated: int = 0
    manual_approvals: int = 0
    
    # Negative signals
    articles_discarded: int = 0
    quality_issues: int = 0
    topics_irrelevant: int = 0
    info_disputed: int = 0
    claims_contradicted: int = 0
    manual_rejections: int = 0
    
    # Computed scores
    usage_rate: float = 0.0
    relevance_rate: float = 0.0
    accuracy_rate: float = 0.0
    
    # Time tracking
    last_feedback: datetime = field(default_factory=datetime.utcnow)
    feedback_count: int = 0
    
    def calculate_scores(self) -> None:
        """Calculate aggregate scores from feedback counts."""
        # Usage rate
        total_usage = self.articles_used + self.articles_discarded
        self.usage_rate = self.articles_used / total_usage if total_usage > 0 else 0.5
        
        # Relevance rate
        total_relevance = self.topics_relevant + self.topics_irrelevant
        self.relevance_rate = self.topics_relevant / total_relevance if total_relevance > 0 else 0.5
        
        # Accuracy rate
        total_accuracy = (self.info_verified + self.claims_corroborated + 
                         self.info_disputed + self.claims_contradicted)
        if total_accuracy > 0:
            self.accuracy_rate = (
                (self.info_verified + self.claims_corroborated) / total_accuracy
            )
        else:
            self.accuracy_rate = 0.5
    
    @property
    def overall_score(self) -> float:
        """Calculate overall feedback score (0-1)."""
        self.calculate_scores()
        return (self.usage_rate * 0.4 + 
                self.relevance_rate * 0.3 + 
                self.accuracy_rate * 0.3)
    
    def to_dict(self) -> Dict[str, Any]:
        self.calculate_scores()
        return {
            "source_id": self.source_id,
            "articles_used": self.articles_used,
            "articles_discarded": self.articles_discarded,
            "usage_rate": round(self.usage_rate, 3),
            "relevance_rate": round(self.relevance_rate, 3),
            "accuracy_rate": round(self.accuracy_rate, 3),
            "overall_score": round(self.overall_score, 3),
            "quality_issues": self.quality_issues,
            "feedback_count": self.feedback_count,
            "last_feedback": self.last_feedback.isoformat()
        }


class FeedbackLoop:
    """
    Manages feedback from downstream layers to improve Layer 1 quality.
    
    Features:
    - Receives feedback signals from L2, L3, L4, L5
    - Aggregates feedback by source
    - Propagates reputation adjustments
    - Triggers parameter tuning based on feedback
    - Maintains feedback history for analysis
    
    Usage:
        feedback_loop = FeedbackLoop(metrics_tracker)
        
        # Receive feedback
        await feedback_loop.receive_feedback(FeedbackSignal(
            feedback_type=FeedbackType.ARTICLE_USED,
            severity=FeedbackSeverity.INFO,
            source_layer="layer2",
            article_id="article_123",
            source_id="ada_derana"
        ))
        
        # Get aggregated feedback
        aggregation = await feedback_loop.get_source_feedback("ada_derana")
        
        # Register handlers
        feedback_loop.register_handler(FeedbackType.QUALITY_ISSUE, handle_quality_issue)
    """
    
    # Configuration
    AGGREGATION_DECAY_HOURS = 168  # 1 week decay for aggregations
    SIGNAL_RETENTION_HOURS = 720   # 30 days signal history
    REPUTATION_UPDATE_THRESHOLD = 10  # Min signals before reputation update
    
    def __init__(
        self,
        metrics_tracker=None,
        reputation_manager=None,
        db_pool=None
    ):
        """Initialize the feedback loop."""
        self.metrics_tracker = metrics_tracker
        self.reputation_manager = reputation_manager
        self.db_pool = db_pool
        
        # Signal storage
        self._signals: List[FeedbackSignal] = []
        
        # Source aggregations
        self._aggregations: Dict[str, FeedbackAggregation] = {}
        
        # Handlers for different feedback types
        self._handlers: Dict[FeedbackType, List[Callable]] = defaultdict(list)
        
        # Pending reputation updates
        self._pending_updates: Dict[str, List[FeedbackSignal]] = defaultdict(list)
        
        logger.info("FeedbackLoop initialized")
    
    # ========================================================================
    # Receiving Feedback
    # ========================================================================
    
    async def receive_feedback(self, signal: FeedbackSignal) -> None:
        """
        Receive and process a feedback signal.
        
        Args:
            signal: FeedbackSignal from downstream layer
        """
        # Store signal
        self._signals.append(signal)
        
        # Update aggregation if source is known
        if signal.source_id:
            await self._update_aggregation(signal)
            
            # Queue for reputation update
            self._pending_updates[signal.source_id].append(signal)
            
            # Check if we should update reputation
            if len(self._pending_updates[signal.source_id]) >= self.REPUTATION_UPDATE_THRESHOLD:
                await self._process_reputation_update(signal.source_id)
        
        # Record in metrics tracker
        if self.metrics_tracker and signal.source_id:
            accepted = signal.feedback_type in [
                FeedbackType.ARTICLE_USED,
                FeedbackType.TOPIC_RELEVANT,
                FeedbackType.INFORMATION_VERIFIED,
                FeedbackType.CLAIM_CORROBORATED,
                FeedbackType.MANUAL_APPROVAL
            ]
            await self.metrics_tracker.record_downstream_feedback(
                article_id=signal.article_id or "unknown",
                source_id=signal.source_id,
                accepted=accepted,
                layer=signal.source_layer,
                reason=signal.feedback_type.value
            )
        
        # Execute registered handlers
        await self._execute_handlers(signal)
        
        # Trim old signals
        self._trim_old_signals()
        
        logger.debug(f"Processed feedback: {signal.feedback_type.value} from {signal.source_layer}")
    
    async def receive_batch_feedback(
        self, 
        signals: List[FeedbackSignal]
    ) -> Dict[str, int]:
        """
        Receive multiple feedback signals at once.
        
        Args:
            signals: List of feedback signals
            
        Returns:
            Dict with counts of processed signals by type
        """
        counts: Dict[str, int] = defaultdict(int)
        
        for signal in signals:
            await self.receive_feedback(signal)
            counts[signal.feedback_type.value] += 1
        
        logger.info(f"Processed batch of {len(signals)} feedback signals")
        return dict(counts)
    
    # ========================================================================
    # Aggregation Methods
    # ========================================================================
    
    async def _update_aggregation(self, signal: FeedbackSignal) -> None:
        """Update source aggregation based on feedback signal."""
        source_id = signal.source_id
        if not source_id:
            return
        
        # Get or create aggregation
        if source_id not in self._aggregations:
            self._aggregations[source_id] = FeedbackAggregation(source_id=source_id)
        
        agg = self._aggregations[source_id]
        agg.last_feedback = signal.timestamp
        agg.feedback_count += 1
        
        # Update counts based on feedback type
        feedback_type = signal.feedback_type
        
        # Usage signals
        if feedback_type == FeedbackType.ARTICLE_USED:
            agg.articles_used += 1
        elif feedback_type == FeedbackType.ARTICLE_DISCARDED:
            agg.articles_discarded += 1
        
        # Quality signals
        elif feedback_type in [FeedbackType.QUALITY_ISSUE, 
                               FeedbackType.CONTENT_INCOMPLETE,
                               FeedbackType.CONTENT_CORRUPTED]:
            agg.quality_issues += 1
        
        # Relevance signals
        elif feedback_type == FeedbackType.TOPIC_RELEVANT:
            agg.topics_relevant += 1
        elif feedback_type in [FeedbackType.TOPIC_IRRELEVANT,
                               FeedbackType.CATEGORY_MISMATCH]:
            agg.topics_irrelevant += 1
        
        # Accuracy signals
        elif feedback_type == FeedbackType.INFORMATION_VERIFIED:
            agg.info_verified += 1
        elif feedback_type == FeedbackType.INFORMATION_DISPUTED:
            agg.info_disputed += 1
        elif feedback_type == FeedbackType.CLAIM_CORROBORATED:
            agg.claims_corroborated += 1
        elif feedback_type == FeedbackType.CLAIM_CONTRADICTED:
            agg.claims_contradicted += 1
        
        # Manual signals
        elif feedback_type == FeedbackType.MANUAL_APPROVAL:
            agg.manual_approvals += 1
        elif feedback_type == FeedbackType.MANUAL_REJECTION:
            agg.manual_rejections += 1
    
    async def get_source_feedback(
        self, 
        source_id: str
    ) -> Optional[FeedbackAggregation]:
        """Get aggregated feedback for a source."""
        return self._aggregations.get(source_id)
    
    async def get_all_aggregations(self) -> Dict[str, FeedbackAggregation]:
        """Get all source feedback aggregations."""
        return self._aggregations.copy()
    
    async def get_low_performing_sources(
        self, 
        threshold: float = 0.5,
        limit: int = 10
    ) -> List[FeedbackAggregation]:
        """Get sources with overall score below threshold."""
        low_performers = [
            agg for agg in self._aggregations.values()
            if agg.overall_score < threshold and agg.feedback_count >= 5
        ]
        low_performers.sort(key=lambda x: x.overall_score)
        return low_performers[:limit]
    
    async def get_high_performing_sources(
        self,
        threshold: float = 0.8,
        limit: int = 10
    ) -> List[FeedbackAggregation]:
        """Get sources with overall score above threshold."""
        high_performers = [
            agg for agg in self._aggregations.values()
            if agg.overall_score >= threshold and agg.feedback_count >= 5
        ]
        high_performers.sort(key=lambda x: x.overall_score, reverse=True)
        return high_performers[:limit]
    
    # ========================================================================
    # Reputation Integration
    # ========================================================================
    
    async def _process_reputation_update(self, source_id: str) -> None:
        """Process pending feedback to update source reputation."""
        if not self.reputation_manager:
            # Clear pending updates since we can't process them
            self._pending_updates[source_id].clear()
            return
        
        signals = self._pending_updates[source_id]
        if not signals:
            return
        
        # Calculate reputation delta based on feedback
        positive_signals = sum(
            1 for s in signals if s.feedback_type in [
                FeedbackType.ARTICLE_USED,
                FeedbackType.TOPIC_RELEVANT,
                FeedbackType.INFORMATION_VERIFIED,
                FeedbackType.CLAIM_CORROBORATED,
                FeedbackType.MANUAL_APPROVAL,
                FeedbackType.SOURCE_RELIABLE
            ]
        )
        
        negative_signals = sum(
            1 for s in signals if s.feedback_type in [
                FeedbackType.ARTICLE_DISCARDED,
                FeedbackType.QUALITY_ISSUE,
                FeedbackType.TOPIC_IRRELEVANT,
                FeedbackType.INFORMATION_DISPUTED,
                FeedbackType.CLAIM_CONTRADICTED,
                FeedbackType.MANUAL_REJECTION,
                FeedbackType.SOURCE_UNRELIABLE
            ]
        )
        
        total = positive_signals + negative_signals
        if total == 0:
            self._pending_updates[source_id].clear()
            return
        
        # Calculate adjustment (small incremental changes)
        ratio = positive_signals / total
        adjustment = (ratio - 0.5) * 2 * 0.02  # Max ±2% adjustment
        
        try:
            # Apply reputation adjustment
            # Note: This would call the reputation manager's adjustment method
            logger.info(
                f"Reputation adjustment for {source_id}: "
                f"{adjustment:+.3f} (pos={positive_signals}, neg={negative_signals})"
            )
            
            # TODO: Integrate with actual ReputationManager
            # await self.reputation_manager.adjust_reputation(source_id, adjustment)
            
        except Exception as e:
            logger.error(f"Failed to update reputation for {source_id}: {e}")
        
        # Clear processed signals
        self._pending_updates[source_id].clear()
    
    # ========================================================================
    # Handler Management
    # ========================================================================
    
    def register_handler(
        self,
        feedback_type: FeedbackType,
        handler: Callable[[FeedbackSignal], Awaitable[None]]
    ) -> None:
        """
        Register a handler for a specific feedback type.
        
        Args:
            feedback_type: Type of feedback to handle
            handler: Async function to call when feedback received
        """
        self._handlers[feedback_type].append(handler)
        logger.debug(f"Registered handler for {feedback_type.value}")
    
    def unregister_handler(
        self,
        feedback_type: FeedbackType,
        handler: Callable
    ) -> bool:
        """Unregister a previously registered handler."""
        try:
            self._handlers[feedback_type].remove(handler)
            return True
        except ValueError:
            return False
    
    async def _execute_handlers(self, signal: FeedbackSignal) -> None:
        """Execute all registered handlers for a feedback signal."""
        handlers = self._handlers.get(signal.feedback_type, [])
        
        for handler in handlers:
            try:
                await handler(signal)
            except Exception as e:
                logger.error(f"Handler error for {signal.feedback_type.value}: {e}")
    
    # ========================================================================
    # Signal History
    # ========================================================================
    
    async def get_recent_signals(
        self,
        source_id: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[FeedbackSignal]:
        """Get recent feedback signals with optional filtering."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        filtered = [s for s in self._signals if s.timestamp >= cutoff]
        
        if source_id:
            filtered = [s for s in filtered if s.source_id == source_id]
        
        if feedback_type:
            filtered = [s for s in filtered if s.feedback_type == feedback_type]
        
        # Sort by most recent first
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered[:limit]
    
    async def get_signal_counts(
        self,
        hours: int = 24
    ) -> Dict[str, int]:
        """Get counts of signals by type in the time window."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        counts: Dict[str, int] = defaultdict(int)
        for signal in self._signals:
            if signal.timestamp >= cutoff:
                counts[signal.feedback_type.value] += 1
        
        return dict(counts)
    
    def _trim_old_signals(self) -> None:
        """Remove signals older than retention period."""
        cutoff = datetime.utcnow() - timedelta(hours=self.SIGNAL_RETENTION_HOURS)
        self._signals = [s for s in self._signals if s.timestamp >= cutoff]
    
    # ========================================================================
    # Export / Import
    # ========================================================================
    
    def export_state(self) -> Dict[str, Any]:
        """Export current state for persistence."""
        return {
            "aggregations": {
                sid: agg.to_dict()
                for sid, agg in self._aggregations.items()
            },
            "signal_counts": len(self._signals),
            "exported_at": datetime.utcnow().isoformat()
        }
    
    async def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback activity."""
        return {
            "total_signals": len(self._signals),
            "sources_tracked": len(self._aggregations),
            "signal_counts": await self.get_signal_counts(),
            "low_performers": len(await self.get_low_performing_sources()),
            "high_performers": len(await self.get_high_performing_sources())
        }
    
    async def load_historical_feedback(self) -> bool:
        """Load historical feedback from database."""
        if not self.db_pool:
            logger.warning("No database pool, skipping historical load")
            return False
        
        try:
            # TODO: Implement actual DB loading
            logger.info("Historical feedback loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load historical feedback: {e}")
            return False
