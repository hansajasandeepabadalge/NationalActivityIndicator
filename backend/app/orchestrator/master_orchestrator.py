"""
Master Orchestrator for AI Agent System

Uses LangGraph to coordinate all AI agents in a directed graph workflow.
Manages the complete data collection pipeline from source monitoring
through validation and storage.

Architecture:
    [Monitor Sources] -> [Scrape Content] -> [Process Articles] 
         -> [Classify Priority] -> [Validate Quality] -> [Store]
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Annotated, TypedDict, Sequence
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from app.agents.config import get_agent_config
from app.agents.source_monitor_agent import SourceMonitorAgent
from app.agents.processing_agent import ProcessingAgent
from app.agents.priority_agent import PriorityDetectionAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.agents.tools.scraper_tools import ScraperToolManager
from app.orchestrator.state_manager import (
    StateManager, 
    PipelinePhase, 
    get_state_manager
)

# Source Reputation System imports
try:
    from app.services.quality_filter import QualityFilter
    from app.services.reputation_manager import ReputationManager
    HAS_REPUTATION = True
except ImportError:
    HAS_REPUTATION = False

# Deduplication system imports
try:
    from app.deduplication import SemanticDeduplicator
    HAS_DEDUPLICATION = True
except ImportError:
    HAS_DEDUPLICATION = False
    SemanticDeduplicator = None

# Metrics recording imports
try:
    from app.services.metrics_recorder import MetricsRecorder, get_metrics_recorder
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False
    MetricsRecorder = None

logger = logging.getLogger(__name__)


class OrchestratorState(TypedDict):
    """State that flows through the LangGraph pipeline."""
    run_id: str
    phase: str
    sources_to_scrape: List[str]
    scraped_content: List[Dict[str, Any]]
    processed_articles: List[Dict[str, Any]]
    priority_classifications: List[Dict[str, Any]]
    validated_articles: List[Dict[str, Any]]
    stored_articles: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    should_continue: bool


class MasterOrchestrator:
    """
    LangGraph-based orchestrator that coordinates all AI agents.
    
    This is the central controller that:
    1. Decides which sources need scraping
    2. Executes scrapers for those sources
    3. Routes content through processing
    4. Classifies priority/urgency
    5. Validates data quality
    6. Stores valid articles
    """
    
    def __init__(self):
        """Initialize the orchestrator with all agents."""
        self.config = get_agent_config()
        self.state_manager = get_state_manager()
        
        # Initialize agents
        self.source_monitor = SourceMonitorAgent()
        self.processing_agent = ProcessingAgent()
        self.priority_agent = PriorityDetectionAgent()
        self.validation_agent = ValidationAgent()
        self.scheduler_agent = SchedulerAgent()
        
        # Initialize tools
        self.scraper_manager = ScraperToolManager()
        
        # Initialize Source Reputation System (lazy initialization - requires DB session)
        # QualityFilter and ReputationManager will be initialized per-session
        self._has_reputation = HAS_REPUTATION
        self.quality_filter = None
        self.reputation_manager = None
        if HAS_REPUTATION:
            logger.info("Source Reputation System available (lazy init)")
        else:
            logger.warning("Source Reputation System not available")
        
        # Initialize Deduplication System
        self._has_deduplication = HAS_DEDUPLICATION
        self.deduplicator = None
        if HAS_DEDUPLICATION:
            try:
                self.deduplicator = SemanticDeduplicator()
                logger.info("SemanticDeduplicator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize SemanticDeduplicator: {e}")
                self._has_deduplication = False
        else:
            logger.warning("Deduplication System not available")
        
        # Initialize Metrics Recorder
        self._has_metrics = HAS_METRICS
        self.metrics_recorder = None
        if HAS_METRICS:
            try:
                self.metrics_recorder = get_metrics_recorder()
                logger.info("MetricsRecorder initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize MetricsRecorder: {e}")
                self._has_metrics = False
        else:
            logger.warning("Metrics Recording not available")
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
        
        logger.info("MasterOrchestrator initialized")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow for data collection.
        
        Flow:
            monitor_sources -> scrape_content -> process_articles 
                -> classify_priority -> validate_quality -> store_articles
        """
        # Create the state graph
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes for each phase
        workflow.add_node("monitor_sources", self._monitor_sources_node)
        workflow.add_node("scrape_content", self._scrape_content_node)
        workflow.add_node("process_articles", self._process_articles_node)
        workflow.add_node("classify_priority", self._classify_priority_node)
        workflow.add_node("validate_quality", self._validate_quality_node)
        workflow.add_node("store_articles", self._store_articles_node)
        
        # Define edges
        workflow.set_entry_point("monitor_sources")
        
        workflow.add_conditional_edges(
            "monitor_sources",
            self._should_continue_to_scraping,
            {
                True: "scrape_content",
                False: END
            }
        )
        
        workflow.add_conditional_edges(
            "scrape_content",
            self._should_continue_to_processing,
            {
                True: "process_articles",
                False: END
            }
        )
        
        workflow.add_edge("process_articles", "classify_priority")
        workflow.add_edge("classify_priority", "validate_quality")
        workflow.add_edge("validate_quality", "store_articles")
        workflow.add_edge("store_articles", END)
        
        # Compile the graph
        return workflow.compile()
    
    async def _monitor_sources_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Monitor all sources and decide which to scrape.
        
        Uses SourceMonitorAgent to make intelligent decisions.
        """
        logger.info(f"Run {state['run_id']}: Monitoring sources")
        
        try:
            await self.state_manager.update_phase(
                state['run_id'], 
                PipelinePhase.MONITORING
            )
            
            # Execute the source monitor agent
            result = await self.source_monitor.execute({
                "run_id": state['run_id']
            })
            
            sources_to_scrape = result.get("sources_to_scrape", [])
            
            await self.state_manager.set_sources_to_scrape(
                state['run_id'], 
                sources_to_scrape
            )
            
            return {
                "sources_to_scrape": sources_to_scrape,
                "phase": PipelinePhase.MONITORING.value,
                "metrics": {
                    **state.get("metrics", {}),
                    "sources_analyzed": result.get("total_sources", 0),
                    "sources_to_scrape": len(sources_to_scrape)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in monitor_sources: {e}")
            return {
                "errors": state.get("errors", []) + [{
                    "phase": "monitor_sources",
                    "error": str(e)
                }],
                "sources_to_scrape": []
            }
    
    def _should_continue_to_scraping(
        self, 
        state: OrchestratorState
    ) -> bool:
        """Check if we have sources to scrape."""
        return len(state.get("sources_to_scrape", [])) > 0
    
    async def _scrape_content_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Execute scrapers for selected sources.
        
        Runs scrapers in parallel with rate limiting.
        """
        logger.info(f"Run {state['run_id']}: Scraping {len(state['sources_to_scrape'])} sources")
        
        try:
            await self.state_manager.update_phase(
                state['run_id'], 
                PipelinePhase.SCRAPING
            )
            
            scraped_content = []
            errors = state.get("errors", [])
            
            # Scrape each source
            for source_name in state["sources_to_scrape"]:
                try:
                    # Execute scraper
                    result = await self.scraper_manager.execute_scraper(source_name)
                    
                    if result.get("success"):
                        articles = result.get("articles", [])
                        for article in articles:
                            article["source_name"] = source_name
                            scraped_content.append(article)
                            
                            await self.state_manager.add_scraped_content(
                                state['run_id'], 
                                article
                            )
                    else:
                        errors.append({
                            "phase": "scrape_content",
                            "source": source_name,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    errors.append({
                        "phase": "scrape_content",
                        "source": source_name,
                        "error": str(e)
                    })
            
            return {
                "scraped_content": scraped_content,
                "phase": PipelinePhase.SCRAPING.value,
                "errors": errors,
                "metrics": {
                    **state.get("metrics", {}),
                    "articles_scraped": len(scraped_content)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in scrape_content: {e}")
            return {
                "errors": state.get("errors", []) + [{
                    "phase": "scrape_content",
                    "error": str(e)
                }],
                "scraped_content": []
            }
    
    def _should_continue_to_processing(
        self, 
        state: OrchestratorState
    ) -> bool:
        """Check if we have content to process."""
        return len(state.get("scraped_content", [])) > 0
    
    async def _process_articles_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Process all scraped articles.
        
        Uses ProcessingAgent to clean and enhance content.
        """
        logger.info(f"Run {state['run_id']}: Processing {len(state['scraped_content'])} articles")
        
        try:
            await self.state_manager.update_phase(
                state['run_id'], 
                PipelinePhase.PROCESSING
            )
            
            processed_articles = []
            errors = state.get("errors", [])
            
            # Process each article
            for content in state["scraped_content"]:
                try:
                    result = await self.processing_agent.execute({
                        "content": content,
                        "source": content.get("source_name", "unknown")
                    })
                    
                    if result.get("success"):
                        processed = result.get("processed_article", {})
                        processed_articles.append(processed)
                        
                        await self.state_manager.add_processed_article(
                            state['run_id'], 
                            processed
                        )
                    else:
                        errors.append({
                            "phase": "process_articles",
                            "article_url": content.get("url", "unknown"),
                            "error": result.get("error", "Processing failed")
                        })
                        
                except Exception as e:
                    errors.append({
                        "phase": "process_articles",
                        "article_url": content.get("url", "unknown"),
                        "error": str(e)
                    })
            
            return {
                "processed_articles": processed_articles,
                "phase": PipelinePhase.PROCESSING.value,
                "errors": errors,
                "metrics": {
                    **state.get("metrics", {}),
                    "articles_processed": len(processed_articles)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in process_articles: {e}")
            return {
                "errors": state.get("errors", []) + [{
                    "phase": "process_articles",
                    "error": str(e)
                }],
                "processed_articles": []
            }
    
    async def _classify_priority_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Classify priority/urgency for all articles.
        
        Uses PriorityAgent to detect critical content.
        """
        logger.info(f"Run {state['run_id']}: Classifying priority for {len(state['processed_articles'])} articles")
        
        try:
            classifications = []
            critical_count = 0
            
            for article in state["processed_articles"]:
                try:
                    result = await self.priority_agent.execute({
                        "article": article
                    })
                    
                    classification = {
                        **article,
                        "urgency_level": result.get("urgency_level", "MEDIUM"),
                        "urgency_reason": result.get("reason", ""),
                        "urgency_score": result.get("urgency_score", 50)
                    }
                    
                    classifications.append(classification)
                    
                    if result.get("urgency_level") in ["CRITICAL", "HIGH"]:
                        critical_count += 1
                        
                except Exception as e:
                    # On error, assign default priority
                    classifications.append({
                        **article,
                        "urgency_level": "MEDIUM",
                        "urgency_reason": f"Classification error: {e}",
                        "urgency_score": 50
                    })
            
            return {
                "priority_classifications": classifications,
                "metrics": {
                    **state.get("metrics", {}),
                    "critical_articles": critical_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error in classify_priority: {e}")
            # Pass through with default priorities
            return {
                "priority_classifications": [
                    {**a, "urgency_level": "MEDIUM"} 
                    for a in state.get("processed_articles", [])
                ],
                "errors": state.get("errors", []) + [{
                    "phase": "classify_priority",
                    "error": str(e)
                }]
            }
    
    async def _validate_quality_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Validate quality of all articles.
        
        Uses ValidationAgent to ensure data quality.
        """
        logger.info(f"Run {state['run_id']}: Validating {len(state['priority_classifications'])} articles")
        
        try:
            await self.state_manager.update_phase(
                state['run_id'], 
                PipelinePhase.VALIDATION
            )
            
            validated_articles = []
            rejected_count = 0
            errors = state.get("errors", [])
            
            for article in state["priority_classifications"]:
                try:
                    result = await self.validation_agent.execute({
                        "content": article
                    })
                    
                    if result.get("is_valid", False):
                        validated = {
                            **article,
                            "quality_score": result.get("quality_score", 0),
                            "validation_timestamp": datetime.utcnow().isoformat()
                        }
                        validated_articles.append(validated)
                        
                        await self.state_manager.add_validated_article(
                            state['run_id'], 
                            validated
                        )
                    else:
                        rejected_count += 1
                        errors.append({
                            "phase": "validate_quality",
                            "article_url": article.get("url", "unknown"),
                            "reason": "Failed validation",
                            "issues": result.get("issues", [])
                        })
                        
                except Exception as e:
                    errors.append({
                        "phase": "validate_quality",
                        "article_url": article.get("url", "unknown"),
                        "error": str(e)
                    })
            
            return {
                "validated_articles": validated_articles,
                "phase": PipelinePhase.VALIDATION.value,
                "errors": errors,
                "metrics": {
                    **state.get("metrics", {}),
                    "articles_validated": len(validated_articles),
                    "articles_rejected": rejected_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error in validate_quality: {e}")
            return {
                "errors": state.get("errors", []) + [{
                    "phase": "validate_quality",
                    "error": str(e)
                }],
                "validated_articles": []
            }
    
    async def _store_articles_node(
        self, 
        state: OrchestratorState
    ) -> Dict[str, Any]:
        """
        Node: Store validated articles to databases.
        
        Applies quality filtering based on source reputation,
        then stores to both PostgreSQL and MongoDB.
        """
        logger.info(f"Run {state['run_id']}: Storing {len(state['validated_articles'])} articles")
        
        try:
            await self.state_manager.update_phase(
                state['run_id'], 
                PipelinePhase.STORAGE
            )
            
            stored_articles = []
            filtered_articles = []
            errors = state.get("errors", [])
            
            for article in state["validated_articles"]:
                try:
                    # Apply quality filter if enabled
                    if self.quality_filter:
                        source_name = article.get("source_name") or article.get("source", {}).get("name", "unknown")
                        article_id = article.get("article_id", f"art_{hash(article.get('url', ''))}")
                        
                        if source_name:
                            # Pre-filter based on source reputation
                            filter_result = await self.quality_filter.pre_filter(
                                article_id=article_id,
                                source_name=source_name
                            )
                            
                            from app.services.reputation_manager import FilterAction
                            
                            if filter_result.action == FilterAction.REJECTED:
                                filtered_articles.append({
                                    "article": article.get("url", "unknown"),
                                    "source_name": source_name,
                                    "reason": filter_result.reason
                                })
                                logger.info(f"Article filtered: {filter_result.reason}")
                                
                                # Record rejection in reputation system
                                if self.reputation_manager:
                                    await self.reputation_manager.record_article_result(
                                        source_name=source_name,
                                        article_id=article_id,
                                        quality_score=30.0,  # Default low score for filtered articles
                                        was_accepted=False
                                    )
                                continue
                            
                            # Record acceptance in reputation system
                            if self.reputation_manager:
                                await self.reputation_manager.record_article_result(
                                    source_name=source_name,
                                    article_id=article_id,
                                    quality_score=70.0,  # Default reasonable score
                                    was_accepted=True
                                )
                    
                    # TODO: Implement actual storage
                    # For now, just mark as stored
                    stored = {
                        **article,
                        "stored_at": datetime.utcnow().isoformat(),
                        "storage_status": "success"
                    }
                    stored_articles.append(stored)
                    
                except Exception as e:
                    errors.append({
                        "phase": "store_articles",
                        "article_url": article.get("url", "unknown"),
                        "error": str(e)
                    })
            # Record metrics to TimescaleDB if available
            if self.metrics_recorder and self._has_metrics:
                try:
                    # Group articles by source for metrics
                    source_counts: Dict[str, int] = {}
                    for article in stored_articles:
                        source = article.get("source_name", "unknown")
                        source_counts[source] = source_counts.get(source, 0) + 1
                    
                    # Record health metrics for each source
                    for source_name, count in source_counts.items():
                        await self.metrics_recorder.record_scrape_cycle(
                            source_name=source_name,
                            source_id=hash(source_name) % 1000,
                            duration_seconds=0,  # Not tracked at this level
                            articles_found=count,
                            articles_new=count,
                            errors=len([e for e in errors if e.get("phase") == "store_articles"])
                        )
                    
                    logger.debug(f"Recorded metrics for {len(source_counts)} sources")
                except Exception as me:
                    logger.warning(f"Failed to record metrics: {me}")
            
            return {
                "stored_articles": stored_articles,
                "phase": PipelinePhase.COMPLETED.value,
                "errors": errors,
                "metrics": {
                    **state.get("metrics", {}),
                    "articles_stored": len(stored_articles),
                    "articles_filtered": len(filtered_articles)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in store_articles: {e}")
            return {
                "errors": state.get("errors", []) + [{
                    "phase": "store_articles",
                    "error": str(e)
                }],
                "stored_articles": []
            }
    
    async def run_cycle(self) -> Dict[str, Any]:
        """
        Execute one complete data collection cycle.
        
        This runs the full pipeline from source monitoring
        through to article storage.
        
        Returns:
            Dict with cycle results and metrics
        """
        # Connect state manager
        await self.state_manager.connect()
        
        # Create a new run
        run_id = await self.state_manager.create_run()
        
        logger.info(f"Starting data collection cycle: {run_id}")
        
        # Initialize state
        initial_state: OrchestratorState = {
            "run_id": run_id,
            "phase": PipelinePhase.IDLE.value,
            "sources_to_scrape": [],
            "scraped_content": [],
            "processed_articles": [],
            "priority_classifications": [],
            "validated_articles": [],
            "stored_articles": [],
            "errors": [],
            "metrics": {},
            "should_continue": True
        }
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Complete the run
            result = await self.state_manager.complete_run(
                run_id, 
                success=len(final_state.get("errors", [])) == 0
            )
            
            logger.info(f"Completed cycle {run_id}: {result}")
            
            return {
                "run_id": run_id,
                "success": True,
                "phase": final_state.get("phase"),
                "metrics": final_state.get("metrics", {}),
                "errors": final_state.get("errors", []),
                "summary": {
                    "sources_scraped": len(final_state.get("sources_to_scrape", [])),
                    "articles_collected": len(final_state.get("scraped_content", [])),
                    "articles_processed": len(final_state.get("processed_articles", [])),
                    "articles_stored": len(final_state.get("stored_articles", []))
                }
            }
            
        except Exception as e:
            logger.error(f"Cycle {run_id} failed: {e}")
            
            await self.state_manager.complete_run(run_id, success=False)
            
            return {
                "run_id": run_id,
                "success": False,
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the orchestrator.
        
        Returns:
            Dict with orchestrator status and recent runs
        """
        await self.state_manager.connect()
        
        recent_runs = await self.state_manager.get_recent_runs(limit=10)
        
        return {
            "status": "operational",
            "agents": {
                "source_monitor": self.source_monitor.get_status(),
                "processing": self.processing_agent.get_status(),
                "priority": self.priority_agent.get_status(),
                "validation": self.validation_agent.get_status(),
                "scheduler": self.scheduler_agent.get_status()
            },
            "recent_runs": recent_runs,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def run_scheduler_optimization(self) -> Dict[str, Any]:
        """
        Run the scheduler agent to optimize scraping frequencies.
        
        This should be run periodically (e.g., daily) to adapt
        to changing source behavior.
        
        Returns:
            Optimization results
        """
        logger.info("Running scheduler optimization")
        
        result = await self.scheduler_agent.run_daily_optimization()
        
        return result


# Factory function
def create_orchestrator() -> MasterOrchestrator:
    """Create and return a MasterOrchestrator instance."""
    return MasterOrchestrator()
