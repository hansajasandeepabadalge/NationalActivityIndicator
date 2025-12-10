"""
Layer 2: Indicator Value Persistence Service

Stores Layer 2 indicator outputs to PostgreSQL for dashboard display.
This bridges the gap between L2 processing (MongoDB) and L5 dashboard (PostgreSQL).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import logging

from app.models.indicator_models import IndicatorDefinition, IndicatorValue
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class Layer2IndicatorPersistence:
    """
    Persists Layer 2 indicator calculations to PostgreSQL.
    
    This service is called after L2 pipeline processing to store
    indicator values for dashboard display.
    """
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._owns_session = False
    
    def _get_session(self) -> Session:
        """Get or create a database session."""
        if self.db is None:
            self.db = SessionLocal()
            self._owns_session = True
        return self.db
    
    def _close_session(self):
        """Close session if we created it."""
        if self._owns_session and self.db:
            self.db.close()
            self.db = None
            self._owns_session = False
    
    def store_indicator_values(
        self,
        indicator_values: List[Dict[str, Any]],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Store L2 indicator values to PostgreSQL.
        
        Args:
            indicator_values: List of indicator value dicts from L2 pipeline
                Each dict should have:
                - indicator_id: str
                - indicator_name: str (optional, for matching)
                - value: float
                - confidence: float
                - article_count: int
                - pestel_category: str (optional)
            timestamp: Optional timestamp (defaults to now)
            
        Returns:
            Dict with stored_count, updated_count, errors
        """
        db = self._get_session()
        ts = timestamp or datetime.utcnow()
        
        stored_count = 0
        updated_count = 0
        errors = []
        
        try:
            for iv in indicator_values:
                try:
                    indicator_id = iv.get('indicator_id')
                    if not indicator_id:
                        # Try to find by name
                        name = iv.get('indicator_name')
                        if name:
                            indicator = db.query(IndicatorDefinition).filter(
                                IndicatorDefinition.indicator_name == name
                            ).first()
                            if indicator:
                                indicator_id = indicator.indicator_id
                    
                    if not indicator_id:
                        errors.append(f"Could not find indicator for: {iv.get('indicator_name', 'unknown')}")
                        continue
                    
                    # Check if indicator exists
                    indicator = db.query(IndicatorDefinition).filter(
                        IndicatorDefinition.indicator_id == indicator_id
                    ).first()
                    
                    if not indicator:
                        errors.append(f"Indicator {indicator_id} not found in definitions")
                        continue
                    
                    # Get value - handle different field names
                    value = iv.get('value')
                    if value is None:
                        value = iv.get('current_value', 0.0)
                    
                    # Get confidence
                    confidence = iv.get('confidence', 1.0)
                    
                    # Get article count / source count
                    source_count = iv.get('article_count', iv.get('source_count', 1))
                    
                    # Upsert the indicator value
                    stmt = insert(IndicatorValue).values(
                        indicator_id=indicator_id,
                        timestamp=ts,
                        value=float(value) if value is not None else 0.0,
                        raw_count=source_count,
                        confidence=float(confidence) if confidence else 1.0,
                        source_count=source_count,
                        extra_metadata={
                            'calculation_type': iv.get('calculation_type'),
                            'matching_articles': iv.get('matching_articles', [])[:10],  # Limit size
                            'subcategory': iv.get('subcategory'),
                            'stored_at': datetime.utcnow().isoformat()
                        }
                    ).on_conflict_do_update(
                        index_elements=['indicator_id', 'timestamp'],
                        set_={
                            'value': float(value) if value is not None else 0.0,
                            'confidence': float(confidence) if confidence else 1.0,
                            'source_count': source_count,
                            'extra_metadata': {
                                'calculation_type': iv.get('calculation_type'),
                                'updated_at': datetime.utcnow().isoformat()
                            }
                        }
                    )
                    
                    result = db.execute(stmt)
                    if result.rowcount > 0:
                        stored_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Error storing {iv.get('indicator_id', 'unknown')}: {str(e)}")
                    logger.error(f"Error storing indicator value: {e}")
            
            db.commit()
            logger.info(f"Stored {stored_count} new, updated {updated_count} indicator values")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in store_indicator_values: {e}")
            errors.append(f"Database error: {str(e)}")
        finally:
            self._close_session()
        
        return {
            'stored_count': stored_count,
            'updated_count': updated_count,
            'total_processed': len(indicator_values),
            'errors': errors
        }
    
    def store_from_layer2_output(
        self,
        layer2_output: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Store indicator values from Layer2Output format.
        
        Args:
            layer2_output: Layer2Output dict with 'indicators' key
            timestamp: Optional timestamp
            
        Returns:
            Storage result dict
        """
        indicators = layer2_output.get('indicators', {})
        
        # Convert from dict format to list format
        indicator_list = []
        for indicator_id, data in indicators.items():
            if isinstance(data, dict):
                indicator_list.append({
                    'indicator_id': indicator_id,
                    **data
                })
            else:
                # Handle IndicatorValueOutput objects
                indicator_list.append({
                    'indicator_id': indicator_id,
                    'indicator_name': getattr(data, 'indicator_name', None),
                    'value': getattr(data, 'value', 0),
                    'confidence': getattr(data, 'confidence', 1.0),
                    'article_count': getattr(data, 'article_count', 0),
                    'pestel_category': getattr(data, 'pestel_category', None),
                    'subcategory': getattr(data, 'subcategory', None),
                })
        
        return self.store_indicator_values(indicator_list, timestamp)


def store_layer2_indicators(
    indicator_values: List[Dict[str, Any]],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Convenience function to store L2 indicator values.
    
    Usage:
        from app.layer2.storage.indicator_persistence import store_layer2_indicators
        
        result = store_layer2_indicators([
            {'indicator_id': 'IND_001', 'value': 65.5, 'confidence': 0.9},
            ...
        ])
    """
    service = Layer2IndicatorPersistence()
    return service.store_indicator_values(indicator_values, timestamp)
