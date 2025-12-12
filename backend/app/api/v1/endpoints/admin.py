"""
Admin API Endpoints for Layer 1 Dashboard

Provides endpoints for monitoring data collection pipeline:
- Data sources status
- Scraping jobs
- Raw articles stream
- Processing pipeline metrics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.models.agent_models import SourceConfig
from app.models.scraping_job import ScrapingJob
from app.models.raw_article import RawArticle as RawArticleModel
from app.models.processed_article import ProcessedArticle

router = APIRouter()


# ==================== Pydantic Schemas ====================

from pydantic import BaseModel

class DataSourceResponse(BaseModel):
    id: int
    name: str
    display_name: str
    source_type: str
    status: str
    base_url: str
    last_scraped: Optional[str] = None
    total_articles: int
    articles_24h: int
    success_rate: float
    avg_articles_per_scrape: float

    class Config:
        from_attributes = True


class ScrapingJobResponse(BaseModel):
    job_id: str
    source_name: str
    status: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[int] = None
    articles_found: int
    articles_processed: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class RawArticleResponse(BaseModel):
    article_id: str
    title: str
    source_name: str
    source_url: str
    scraped_at: str
    publish_date: Optional[str] = None
    author: Optional[str] = None
    word_count: Optional[int] = None
    language: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineStageResponse(BaseModel):
    name: str
    count: int
    processing_rate: float
    success_rate: float
    error_count: int
    avg_processing_time: float


class RetryJobResponse(BaseModel):
    success: bool
    message: str


# ==================== Endpoints ====================

@router.get("/sources", response_model=List[DataSourceResponse])
async def get_data_sources(
    db: Session = Depends(get_db)
):
    """
    Get all data sources with their current status and statistics.
    
    Returns:
        List of data sources with metrics including:
        - Last scrape time
        - Total articles scraped
        - Articles scraped in last 24 hours
        - Success rate
        - Average articles per scrape
    """
    try:
        # Get all source configs
        sources = db.query(SourceConfig).all()
        
        result = []
        for source in sources:
            # Calculate statistics for each source
            # Last scrape time
            last_job = db.query(ScrapingJob).filter(
                ScrapingJob.source_id == source.id
            ).order_by(desc(ScrapingJob.created_at)).first()
            
            last_scraped = None
            if last_job:
                time_diff = datetime.utcnow() - last_job.created_at
                if time_diff.total_seconds() < 60:
                    last_scraped = f"{int(time_diff.total_seconds())} sec ago"
                elif time_diff.total_seconds() < 3600:
                    last_scraped = f"{int(time_diff.total_seconds() / 60)} min ago"
                else:
                    last_scraped = f"{int(time_diff.total_seconds() / 3600)} hour ago"
            
            # Total articles (assuming we have a way to count them)
            # This would need to be adjusted based on your actual data model
            total_articles = db.query(func.count(RawArticleModel.id)).filter(
                RawArticleModel.source_name == source.name
            ).scalar() or 0
            
            # Articles in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            articles_24h = db.query(func.count(RawArticleModel.id)).filter(
                RawArticleModel.source_name == source.name,
                RawArticleModel.scraped_at >= yesterday
            ).scalar() or 0
            
            # Success rate (from scraping jobs)
            total_jobs = db.query(func.count(ScrapingJob.id)).filter(
                ScrapingJob.source_id == source.id
            ).scalar() or 0
            
            successful_jobs = db.query(func.count(ScrapingJob.id)).filter(
                ScrapingJob.source_id == source.id,
                ScrapingJob.status == 'completed'
            ).scalar() or 0
            
            success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Average articles per scrape
            avg_articles = db.query(func.avg(ScrapingJob.articles_found)).filter(
                ScrapingJob.source_id == source.id,
                ScrapingJob.status == 'completed'
            ).scalar() or 0
            
            # Determine status
            status = 'active' if source.is_active else 'inactive'
            if last_job and last_job.status == 'failed':
                status = 'error'
            
            result.append(DataSourceResponse(
                id=source.id,
                name=source.name,
                display_name=source.display_name or source.name,
                source_type=source.source_type or 'news',
                status=status,
                base_url=source.base_url,
                last_scraped=last_scraped,
                total_articles=total_articles,
                articles_24h=articles_24h,
                success_rate=round(success_rate, 1),
                avg_articles_per_scrape=round(float(avg_articles or 0), 1)
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data sources: {str(e)}")


@router.get("/scraping-jobs", response_model=List[ScrapingJobResponse])
async def get_scraping_jobs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get recent scraping jobs with their status and metrics.
    
    Args:
        limit: Maximum number of jobs to return (default: 50, max: 200)
    
    Returns:
        List of recent scraping jobs with status, timing, and article counts
    """
    try:
        jobs = db.query(ScrapingJob).order_by(
            desc(ScrapingJob.created_at)
        ).limit(limit).all()
        
        result = []
        for job in jobs:
            # Get source name
            source = db.query(SourceConfig).filter(SourceConfig.id == job.source_id).first()
            source_name = source.display_name if source else "Unknown"
            
            # Calculate time ago for start_time
            time_diff = datetime.utcnow() - job.created_at
            if time_diff.total_seconds() < 60:
                start_time = f"{int(time_diff.total_seconds())} sec ago"
            elif time_diff.total_seconds() < 3600:
                start_time = f"{int(time_diff.total_seconds() / 60)} min ago"
            else:
                start_time = f"{int(time_diff.total_seconds() / 3600)} hour ago"
            
            # End time
            end_time = None
            if job.completed_at:
                end_diff = datetime.utcnow() - job.completed_at
                if end_diff.total_seconds() < 60:
                    end_time = f"{int(end_diff.total_seconds())} sec ago"
                elif end_diff.total_seconds() < 3600:
                    end_time = f"{int(end_diff.total_seconds() / 60)} min ago"
                else:
                    end_time = f"{int(end_diff.total_seconds() / 3600)} hour ago"
            
            # Duration
            duration_seconds = None
            if job.completed_at and job.created_at:
                duration_seconds = int((job.completed_at - job.created_at).total_seconds())
            
            result.append(ScrapingJobResponse(
                job_id=str(job.id),
                source_name=source_name,
                status=job.status or 'pending',
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                articles_found=job.articles_found or 0,
                articles_processed=job.articles_processed or 0,
                error_message=job.error_message
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scraping jobs: {str(e)}")


@router.get("/raw-articles", response_model=List[RawArticleResponse])
async def get_raw_articles(
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get raw articles stream with optional filtering by source.
    
    Args:
        source: Optional source name to filter by
        limit: Maximum number of articles to return (default: 50, max: 200)
    
    Returns:
        List of raw articles with metadata
    """
    try:
        query = db.query(RawArticleModel).order_by(desc(RawArticleModel.scraped_at))
        
        if source and source != 'all':
            query = query.filter(RawArticleModel.source_name == source)
        
        articles = query.limit(limit).all()
        
        result = []
        for article in articles:
            # Calculate time ago
            time_diff = datetime.utcnow() - article.scraped_at
            if time_diff.total_seconds() < 60:
                scraped_at = f"{int(time_diff.total_seconds())} sec ago"
            elif time_diff.total_seconds() < 3600:
                scraped_at = f"{int(time_diff.total_seconds() / 60)} min ago"
            else:
                scraped_at = f"{int(time_diff.total_seconds() / 3600)} hour ago"
            
            # Publish date
            publish_date = None
            if article.publish_date:
                pub_diff = datetime.utcnow() - article.publish_date
                if pub_diff.total_seconds() < 3600:
                    publish_date = f"{int(pub_diff.total_seconds() / 60)} min ago"
                else:
                    publish_date = f"{int(pub_diff.total_seconds() / 3600)} hour ago"
            
            result.append(RawArticleResponse(
                article_id=article.article_id,
                title=article.title or "No title",
                source_name=article.source_name,
                source_url=article.url or "",
                scraped_at=scraped_at,
                publish_date=publish_date,
                author=article.author,
                word_count=article.word_count,
                language=article.language or 'en'
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching raw articles: {str(e)}")


@router.get("/pipeline-status", response_model=List[PipelineStageResponse])
async def get_pipeline_status(
    db: Session = Depends(get_db)
):
    """
    Get processing pipeline status with metrics for each stage.
    
    Returns:
        List of pipeline stages with counts, rates, and success metrics
    """
    try:
        # Count articles at each stage
        total_raw = db.query(func.count(RawArticleModel.id)).scalar() or 0
        total_processed = db.query(func.count(ProcessedArticle.id)).scalar() or 0
        
        # Calculate rates (articles per hour) based on recent activity
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        raw_last_hour = db.query(func.count(RawArticleModel.id)).filter(
            RawArticleModel.scraped_at >= one_hour_ago
        ).scalar() or 0
        
        processed_last_hour = db.query(func.count(ProcessedArticle.id)).filter(
            ProcessedArticle.created_at >= one_hour_ago
        ).scalar() or 0
        
        # Mock pipeline stages (adjust based on your actual pipeline)
        stages = [
            PipelineStageResponse(
                name="Raw Scraped",
                count=total_raw,
                processing_rate=raw_last_hour,
                success_rate=100.0,
                error_count=0,
                avg_processing_time=0.0
            ),
            PipelineStageResponse(
                name="Validated",
                count=int(total_raw * 0.99),
                processing_rate=raw_last_hour * 0.99,
                success_rate=99.1,
                error_count=int(total_raw * 0.01),
                avg_processing_time=0.8
            ),
            PipelineStageResponse(
                name="Translated",
                count=int(total_raw * 0.93),
                processing_rate=raw_last_hour * 0.93,
                success_rate=94.0,
                error_count=int(total_raw * 0.06),
                avg_processing_time=2.5
            ),
            PipelineStageResponse(
                name="Cleaned",
                count=int(total_raw * 0.925),
                processing_rate=raw_last_hour * 0.925,
                success_rate=99.4,
                error_count=int(total_raw * 0.005),
                avg_processing_time=1.2
            ),
            PipelineStageResponse(
                name="Processed",
                count=total_processed,
                processing_rate=processed_last_hour,
                success_rate=99.4,
                error_count=int(total_raw * 0.005),
                avg_processing_time=3.5
            )
        ]
        
        return stages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pipeline status: {str(e)}")


@router.post("/scraping-jobs/{job_id}/retry", response_model=RetryJobResponse)
async def retry_scraping_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Retry a failed scraping job.
    
    Args:
        job_id: ID of the job to retry
    
    Returns:
        Success status and message
    """
    try:
        # Find the job
        job = db.query(ScrapingJob).filter(ScrapingJob.id == int(job_id)).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != 'failed':
            return RetryJobResponse(
                success=False,
                message=f"Job is not in failed state (current status: {job.status})"
            )
        
        # Reset job status to pending for retry
        job.status = 'pending'
        job.error_message = None
        db.commit()
        
        # TODO: Trigger actual scraping job execution
        # This would typically involve:
        # 1. Adding job to a task queue (Celery, RQ, etc.)
        # 2. Or calling the scraper directly
        
        return RetryJobResponse(
            success=True,
            message=f"Job {job_id} has been queued for retry"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error retrying job: {str(e)}")
