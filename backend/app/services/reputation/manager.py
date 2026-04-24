import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.services.reputation.config import (
    ReputationConfig, 
    ReputationTier, 
    FilterAction, 
    FilterResult, 
    ReputationUpdate,
    ConfigurationLoader
)
from app.services.reputation.repository import ReputationRepository
from app.services.reputation.calculator import ReputationCalculator
from app.services.reputation.tasks import ReputationTasks

logger = logging.getLogger(__name__)

class ReputationManager:
    """
    Facade managing source reputation scoring and updates.
    Delegates to Config, Repository, Calculator, and Task engines.
    """
    
    def __init__(self, db: Session, config: Optional[ReputationConfig] = None):
        self.db = db
        # If config is passed, assume it's pre-loaded, else initialize loader
        if config:
            self.config = config
            self.loader = None
        else:
            self.config = ReputationConfig()
            self.loader = ConfigurationLoader(self.db, self.config)
            
        self.repository = ReputationRepository(self.db)
        self.calculator = None
        self.tasks = None

    async def _ensure_loaded(self):
        if self.loader:
            self.config = self.loader.load()
        if not self.calculator:
            self.calculator = ReputationCalculator(self.db, self.config, self.repository)
        if not self.tasks:
            self.tasks = ReputationTasks(self.db, self.config, self.repository)

    async def get_or_create_source(
        self, 
        source_name: str,
        source_url: Optional[str] = None,
        source_type: str = "news",
        initial_credibility: float = 0.75
    ) -> Any:
        await self._ensure_loaded()
        return await self.repository.get_or_create_source(source_name, source_url, source_type, initial_credibility)

    async def get_source_reputation(self, source_name: str) -> Optional[float]:
        return await self.repository.get_source_reputation(source_name)

    async def is_source_active(self, source_name: str) -> bool:
        await self._ensure_loaded()
        from app.models.source_reputation_models import SourceReputation
        source = self.db.query(SourceReputation).filter(SourceReputation.source_name == source_name).first()
        
        if not source:
            return True
            
        if not source.is_active:
            return False
            
        if source.is_manually_overridden and source.override_until:
            if source.override_until > datetime.utcnow():
                return source.is_active
                
        return source.reputation_score >= self.config.min_reputation_active

    async def record_article_result(
        self,
        source_name: str,
        article_id: str,
        quality_score: float,
        was_accepted: bool,
        confidence_score: Optional[float] = None,
        classification_correct: Optional[bool] = None
    ) -> ReputationUpdate:
        await self._ensure_loaded()
        return await self.calculator.process_article_result(
            source_name, article_id, quality_score, was_accepted, confidence_score, classification_correct
        )

    async def get_weight_multiplier(self, source_name: str) -> float:
        await self._ensure_loaded()
        from app.models.source_reputation_models import SourceReputation
        source = self.db.query(SourceReputation).filter(SourceReputation.source_name == source_name).first()
        
        if not source:
            return 1.0
            
        tier = ReputationTier(source.reputation_tier)
        return self.config.weight_multipliers.get(tier, 1.0)

    async def create_daily_snapshot(self, source_name: str) -> None:
        await self._ensure_loaded()
        await self.tasks.create_daily_snapshot(source_name)

    async def apply_inactivity_decay(self) -> List[ReputationUpdate]:
        await self._ensure_loaded()
        return await self.tasks.apply_inactivity_decay()

    async def get_sources_by_tier(self, tier: ReputationTier) -> List[Dict[str, Any]]:
        return await self.repository.get_sources_by_tier(tier)

    async def get_reputation_summary(self) -> Dict[str, Any]:
        await self._ensure_loaded()
        config_dict = {
            "min_reputation_active": self.config.min_reputation_active,
            "min_article_quality": self.config.min_article_quality,
            "boost_rate": self.config.boost_rate,
            "penalty_rate": self.config.penalty_rate
        }
        return await self.repository.get_reputation_summary(config_dict)

    async def manually_override_source(
        self,
        source_name: str,
        is_active: bool,
        reason: str,
        override_by: str,
        duration_days: Optional[int] = None
    ) -> None:
        await self._ensure_loaded()
        await self.repository.manually_override_source(source_name, is_active, reason, override_by, duration_days)

def create_reputation_manager(
    db: Session,
    config: Optional[ReputationConfig] = None
) -> ReputationManager:
    """Create a ReputationManager instance."""
    return ReputationManager(db=db, config=config)
