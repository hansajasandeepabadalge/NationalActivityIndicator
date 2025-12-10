"""
Tests for Source Reputation System

Tests for:
- ReputationManager service
- QualityFilter service
- API endpoints
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

# Test ReputationManager
class TestReputationManager:
    """Tests for ReputationManager service."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.query.return_value.filter.return_value.all.return_value = []
        return db
    
    @pytest.fixture
    def manager(self, mock_db):
        """Create ReputationManager instance with mock DB."""
        from app.services.reputation_manager import ReputationManager, ReputationConfig
        return ReputationManager(db=mock_db, config=ReputationConfig())
    
    def test_score_to_tier_platinum(self, manager):
        """Test tier classification for platinum."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.95) == ReputationTier.PLATINUM
        assert manager._score_to_tier(0.90) == ReputationTier.PLATINUM
    
    def test_score_to_tier_gold(self, manager):
        """Test tier classification for gold."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.85) == ReputationTier.GOLD
        assert manager._score_to_tier(0.75) == ReputationTier.GOLD
    
    def test_score_to_tier_silver(self, manager):
        """Test tier classification for silver."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.70) == ReputationTier.SILVER
        assert manager._score_to_tier(0.60) == ReputationTier.SILVER
    
    def test_score_to_tier_bronze(self, manager):
        """Test tier classification for bronze."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.55) == ReputationTier.BRONZE
        assert manager._score_to_tier(0.45) == ReputationTier.BRONZE
    
    def test_score_to_tier_probation(self, manager):
        """Test tier classification for probation."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.40) == ReputationTier.PROBATION
        assert manager._score_to_tier(0.30) == ReputationTier.PROBATION
    
    def test_score_to_tier_blacklisted(self, manager):
        """Test tier classification for blacklisted."""
        from app.services.reputation_manager import ReputationTier
        assert manager._score_to_tier(0.25) == ReputationTier.BLACKLISTED
        assert manager._score_to_tier(0.0) == ReputationTier.BLACKLISTED
    
    def test_tier_to_weight_multiplier(self, manager):
        """Test weight multipliers by tier."""
        from app.services.reputation_manager import ReputationTier
        
        assert manager._tier_to_weight_multiplier(ReputationTier.PLATINUM) == 1.3
        assert manager._tier_to_weight_multiplier(ReputationTier.GOLD) == 1.15
        assert manager._tier_to_weight_multiplier(ReputationTier.SILVER) == 1.0
        assert manager._tier_to_weight_multiplier(ReputationTier.BRONZE) == 0.85
        assert manager._tier_to_weight_multiplier(ReputationTier.PROBATION) == 0.7
        assert manager._tier_to_weight_multiplier(ReputationTier.BLACKLISTED) == 0.0


# Test QualityFilter
class TestQualityFilter:
    """Tests for QualityFilter service."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def filter_service(self, mock_db):
        """Create QualityFilter instance with mock DB."""
        from app.services.quality_filter import QualityFilter, FilterConfig
        config = FilterConfig(enabled=True, soft_mode=False)
        return QualityFilter(db=mock_db, config=config)
    
    def test_filter_config_defaults(self):
        """Test FilterConfig default values."""
        from app.services.quality_filter import FilterConfig
        
        config = FilterConfig()
        assert config.enabled == True
        assert config.pre_filter_enabled == True
        assert config.post_filter_enabled == True
        assert config.min_quality_score == 40.0
        assert config.soft_mode == False
    
    def test_filter_stats_acceptance_rate(self):
        """Test FilterStats acceptance rate calculation."""
        from app.services.quality_filter import FilterStats
        
        stats = FilterStats()
        stats.accepted = 80
        stats.rejected = 20
        
        assert stats.acceptance_rate() == 0.8
    
    def test_filter_stats_acceptance_rate_zero(self):
        """Test FilterStats acceptance rate with zero articles."""
        from app.services.quality_filter import FilterStats
        
        stats = FilterStats()
        assert stats.acceptance_rate() == 1.0
    
    def test_filter_stats_to_dict(self):
        """Test FilterStats serialization."""
        from app.services.quality_filter import FilterStats
        
        stats = FilterStats()
        stats.total_processed = 100
        stats.accepted = 80
        stats.rejected = 20
        
        result = stats.to_dict()
        
        assert result['total_processed'] == 100
        assert result['accepted'] == 80
        assert result['rejected'] == 20
        assert result['acceptance_rate'] == 0.8


# Test Models
class TestSourceReputationModels:
    """Tests for source reputation models."""
    
    def test_reputation_tier_enum(self):
        """Test ReputationTier enum values."""
        from app.models.source_reputation_models import ReputationTier
        
        assert ReputationTier.PLATINUM.value == "platinum"
        assert ReputationTier.GOLD.value == "gold"
        assert ReputationTier.SILVER.value == "silver"
        assert ReputationTier.BRONZE.value == "bronze"
        assert ReputationTier.PROBATION.value == "probation"
        assert ReputationTier.BLACKLISTED.value == "blacklisted"
    
    def test_filter_action_enum(self):
        """Test FilterAction enum values."""
        from app.models.source_reputation_models import FilterAction
        
        assert FilterAction.ACCEPTED.value == "accepted"
        assert FilterAction.REJECTED.value == "rejected"
        assert FilterAction.FLAGGED.value == "flagged"
        assert FilterAction.BOOSTED.value == "boosted"
        assert FilterAction.DOWNGRADED.value == "downgraded"
    
    def test_default_thresholds(self):
        """Test that default thresholds are defined."""
        from app.models.source_reputation_models import DEFAULT_THRESHOLDS
        
        assert len(DEFAULT_THRESHOLDS) >= 5
        
        threshold_names = [t['threshold_name'] for t in DEFAULT_THRESHOLDS]
        assert "MIN_REPUTATION_ACTIVE" in threshold_names
        assert "MIN_ARTICLE_QUALITY" in threshold_names
        assert "REPUTATION_BOOST_RATE" in threshold_names


# Test FilterResult
class TestFilterResult:
    """Tests for FilterResult dataclass."""
    
    def test_filter_result_to_dict(self):
        """Test FilterResult serialization."""
        from app.services.reputation_manager import FilterResult, FilterAction
        
        result = FilterResult(
            action=FilterAction.ACCEPTED,
            reason="Test reason",
            weight_multiplier=1.15,
            source_reputation=0.85,
            article_quality=75.5,
            processing_time_ms=10
        )
        
        data = result.to_dict()
        
        assert data['action'] == 'accepted'
        assert data['reason'] == "Test reason"
        assert data['weight_multiplier'] == 1.15
        assert data['source_reputation'] == 0.85
        assert data['article_quality'] == 75.5
        assert data['processing_time_ms'] == 10


# Test ReputationUpdate
class TestReputationUpdate:
    """Tests for ReputationUpdate dataclass."""
    
    def test_reputation_update_to_dict(self):
        """Test ReputationUpdate serialization."""
        from app.services.reputation_manager import ReputationUpdate
        
        update = ReputationUpdate(
            source_name="Test Source",
            old_score=0.75,
            new_score=0.78,
            old_tier="silver",
            new_tier="gold",
            change_reason="High quality article",
            tier_changed=True
        )
        
        data = update.to_dict()
        
        assert data['source_name'] == "Test Source"
        assert data['old_score'] == 0.75
        assert data['new_score'] == 0.78
        assert data['score_change'] == 0.03
        assert data['tier_changed'] == True


# Integration Tests (requires database)
class TestReputationIntegration:
    """Integration tests requiring database connection."""
    
    @pytest.mark.skip(reason="Requires database connection")
    @pytest.mark.asyncio
    async def test_create_source_reputation(self):
        """Test creating a new source reputation."""
        from app.services.reputation_manager import create_reputation_manager
        from app.db.session import get_db_session
        
        async with get_db_session() as db:
            manager = create_reputation_manager(db)
            
            source = await manager.get_or_create_source(
                source_name="Test News",
                source_type="news",
                initial_credibility=0.8
            )
            
            assert source.source_name == "Test News"
            assert source.reputation_score == 0.8
            assert source.reputation_tier == "gold"
    
    @pytest.mark.skip(reason="Requires database connection")
    @pytest.mark.asyncio
    async def test_record_article_result(self):
        """Test recording article processing result."""
        from app.services.reputation_manager import create_reputation_manager
        from app.db.session import get_db_session
        
        async with get_db_session() as db:
            manager = create_reputation_manager(db)
            
            # Record high quality article
            update = await manager.record_article_result(
                source_name="Test News",
                article_id="test_001",
                quality_score=90.0,
                was_accepted=True
            )
            
            assert update.new_score > update.old_score
            assert "High quality" in update.change_reason or "Excellent" in update.change_reason


# Test API Endpoints
class TestReputationAPI:
    """Tests for reputation API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    
    @pytest.mark.skip(reason="Requires running server")
    def test_health_endpoint(self, client):
        """Test reputation health endpoint."""
        response = client.get("/api/v1/reputation/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    @pytest.mark.skip(reason="Requires running server")
    def test_list_sources(self, client):
        """Test list sources endpoint."""
        response = client.get("/api/v1/reputation/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.skip(reason="Requires running server")
    def test_get_summary(self, client):
        """Test reputation summary endpoint."""
        response = client.get("/api/v1/reputation/summary")
        assert response.status_code == 200
        data = response.json()
        assert 'total_sources' in data
        assert 'tier_distribution' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
