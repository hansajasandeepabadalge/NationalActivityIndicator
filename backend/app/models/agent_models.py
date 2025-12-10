"""
AI Agent Database Models

SQLAlchemy models for storing agent decisions, scraping schedules,
urgency classifications, and quality validations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class UrgencyLevel(str, enum.Enum):
    """Urgency classification levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriorityLevel(str, enum.Enum):
    """Source priority levels"""
    CRITICAL = "critical"  # DMC, Weather alerts - every 5 min
    HIGH = "high"  # Major news - every 15 min
    MEDIUM = "medium"  # Provincial news - every 1 hour
    LOW = "low"  # Research, historical - daily


class AgentDecision(Base):
    """
    Stores all AI agent decisions for auditing and learning.
    
    Every decision made by any agent is logged here with full context,
    enabling analysis, debugging, and future improvements.
    """
    __tablename__ = "agent_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    decision_type = Column(String(50), nullable=False, index=True)
    
    # Input/Output data
    input_data = Column(JSONB, nullable=True)
    output_decision = Column(JSONB, nullable=True)
    reasoning = Column(Text, nullable=True)
    
    # LLM details
    llm_provider = Column(String(50), nullable=True)  # groq, together, openai
    llm_model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AgentDecision {self.agent_name}:{self.decision_type} at {self.created_at}>"


class ScrapingSchedule(Base):
    """
    Dynamic scraping schedule for each source.
    
    The Scheduler Agent updates these values based on source behavior patterns
    to optimize resource usage while ensuring timely data collection.
    """
    __tablename__ = "scraping_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, nullable=False, index=True)
    source_url = Column(String(500), nullable=True)
    
    # Scheduling
    frequency_minutes = Column(Integer, default=60)  # How often to scrape
    priority_level = Column(String(20), default="medium")
    is_active = Column(Boolean, default=True)
    
    # Tracking
    last_scraped = Column(DateTime, nullable=True)
    last_articles_count = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    total_articles_scraped = Column(Integer, default=0)
    
    # Source quality metrics
    avg_articles_per_scrape = Column(Float, default=0.0)
    reliability_score = Column(Float, default=1.0)  # 0-1
    
    # Management
    updated_by = Column(String(50), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScrapingSchedule {self.source_name}: every {self.frequency_minutes}min>"


class UrgencyClassification(Base):
    """
    Stores urgency classifications for processed content.
    
    The Priority Agent classifies each piece of content to determine
    processing priority and trigger alerts for critical items.
    """
    __tablename__ = "urgency_classifications"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(100), nullable=False, index=True)  # Reference to article
    
    # Classification
    urgency_level = Column(String(20), nullable=False, index=True)  # critical/high/medium/low
    urgency_score = Column(Float, default=0.5)  # 0-1 confidence
    
    # Signals detected
    detected_signals = Column(ARRAY(String), default=[])  # Keywords/patterns found
    classification_reasoning = Column(Text, nullable=True)
    
    # Processing
    processing_priority = Column(Integer, default=100)  # Lower = higher priority
    fast_tracked = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    
    # Validation (for learning)
    human_confirmed = Column(Boolean, nullable=True)
    human_feedback = Column(Text, nullable=True)
    
    # Timestamps
    classified_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<UrgencyClassification {self.content_id}: {self.urgency_level}>"


class QualityValidation(Base):
    """
    Stores quality validation results for processed content.
    
    The Validation Agent checks each piece of content before storage,
    flagging issues and suggesting corrections.
    """
    __tablename__ = "quality_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String(100), nullable=False, index=True)
    
    # Validation results
    is_valid = Column(Boolean, default=True)
    quality_score = Column(Float, default=0.0)  # 0-100
    
    # Issues found
    validation_issues = Column(JSONB, default=[])  # List of issues
    auto_corrections = Column(JSONB, default={})  # Applied corrections
    
    # Review status
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Cross-validation
    cross_validated = Column(Boolean, default=False)
    matching_sources = Column(Integer, default=0)
    
    # Timestamps
    validated_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<QualityValidation {self.content_id}: score={self.quality_score}>"


class AgentMetrics(Base):
    """
    Daily aggregated metrics for each agent.
    
    Used for monitoring performance, tracking costs, and identifying
    optimization opportunities.
    """
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Date of metrics
    
    # Performance
    decisions_made = Column(Integer, default=0)
    successful_decisions = Column(Integer, default=0)
    failed_decisions = Column(Integer, default=0)
    avg_latency_ms = Column(Integer, default=0)
    max_latency_ms = Column(Integer, default=0)
    
    # Token usage
    total_tokens_used = Column(Integer, default=0)
    
    # Cost (should be $0 with Groq!)
    cost_usd = Column(Float, default=0.0)
    
    # Provider breakdown
    groq_requests = Column(Integer, default=0)
    together_requests = Column(Integer, default=0)
    openai_requests = Column(Integer, default=0)
    
    # Quality (if applicable)
    accuracy_rate = Column(Float, nullable=True)  # Based on human feedback
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    class Meta:
        unique_together = [['agent_name', 'date']]
    
    def __repr__(self):
        return f"<AgentMetrics {self.agent_name} on {self.date}: {self.decisions_made} decisions>"


class SourceConfig(Base):
    """
    Configuration for each data source.
    
    Stores static configuration for the 26+ sources, including
    scraper settings, priority, and categorization.
    
    The 'selectors' JSONB field enables universal configurable scraping:
    {
        "list_url": "https://example.com/news",
        "article_link_pattern": "/news/\\d+",
        "title": "h1.article-title",
        "body": "div.article-content",
        "date": "span.publish-date",
        "author": "span.author-name",
        "image": "div.article-content img"
    }
    """
    __tablename__ = "source_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), unique=True, nullable=False, index=True)  # Primary identifier
    
    # Source details
    base_url = Column(String(500), nullable=False)
    source_type = Column(String(50), default="news")  # news, government, social, financial
    language = Column(String(10), default="en")  # en, si, ta
    country = Column(String(10), default="LK")  # Country code
    
    # Categorization
    categories = Column(ARRAY(String), nullable=True)  # Array of categories
    reliability_tier = Column(String(20), default="standard")  # standard, trusted, premium
    
    # Scraper configuration
    scraper_class = Column(String(100), nullable=True)  # e.g., "AdaDeranaScraper" or "ConfigurableScraper"
    
    # Universal scraper selectors (CSS selectors for extracting content)
    selectors = Column(JSONB, nullable=True)  # CSS selectors for title, body, date, etc.
    
    # Rate limiting
    rate_limit_requests = Column(Integer, default=10)  # Max requests per period
    rate_limit_period = Column(Integer, default=60)  # Period in seconds
    
    # JavaScript rendering requirement
    requires_javascript = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Additional config stored as JSON (note: 'metadata' is reserved in SQLAlchemy)
    config_metadata = Column('metadata', JSONB, nullable=True)  # Maps to 'metadata' column in DB
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Convenience properties
    @property
    def name(self) -> str:
        """Alias for source_name for backward compatibility."""
        return self.source_name
    
    @property
    def display_name(self) -> str:
        """Get display name from config_metadata or use source_name."""
        if self.config_metadata and "display_name" in self.config_metadata:
            return self.config_metadata["display_name"]
        return self.source_name.replace("_", " ").title()
    
    @property
    def priority_level(self) -> str:
        """Get priority level from config_metadata."""
        if self.config_metadata and "priority_level" in self.config_metadata:
            return self.config_metadata["priority_level"]
        return "medium"
    
    @property
    def category(self) -> str:
        """Get first category or None."""
        if self.categories:
            return self.categories[0]
        return None
    
    def __repr__(self):
        return f"<SourceConfig {self.source_name}: {self.source_type}>"
    
    def get_selectors(self) -> dict:
        """Get selectors with defaults."""
        default_selectors = {
            "list_url": None,
            "article_link_pattern": None,
            "title": "h1",
            "body": "article, .content, .article-body, main",
            "date": ".date, .publish-date, time",
            "author": ".author, .byline",
            "image": "article img, .content img"
        }
        if self.selectors:
            default_selectors.update(self.selectors)
        return default_selectors
