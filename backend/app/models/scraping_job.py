"""
Scraping Job Database Model

Tracks scraping job execution, status, and metrics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ScrapingJob(Base):
    """
    Tracks individual scraping job executions.
    
    Each time a source is scraped, a job record is created to track:
    - Job status (pending, running, completed, failed)
    - Articles found and processed
    - Execution timing
    - Error messages if failed
    """
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source_configs.id"), nullable=False, index=True)
    
    # Job status
    status = Column(String(20), default="pending", index=True)  # pending, running, completed, failed
    
    # Metrics
    articles_found = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    # source = relationship("SourceConfig", back_populates="scraping_jobs")
    
    def __repr__(self):
        return f"<ScrapingJob {self.id}: {self.status} - {self.articles_processed}/{self.articles_found}>"
