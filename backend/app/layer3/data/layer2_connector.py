"""
Layer 2 Data Connector for Layer 3

Fetches national indicators from Layer 2 databases (PostgreSQL + MongoDB)
Replaces MockDataLoader with real data integration
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class Layer2Connector:
    """
    Connects to Layer 2 databases and fetches national indicators
    
    Replaces MockDataLoader with real database integration
    """
    
    def __init__(self):
        """Initialize database connections"""
        # PostgreSQL connection (TimescaleDB for indicator values)
        self.pg_config = {
            'host': '127.0.0.1',
            'port': 15432,
            'database': 'national_indicator',
            'user': 'postgres',
            'password': 'postgres_secure_2024'
        }
        
        # MongoDB connection (for detailed calculations)
        self.mongo_uri = 'mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'
        self.mongo_db = 'national_indicator'
        
        logger.info("Layer2Connector initialized")
    
    def get_latest_national_indicators(self) -> Dict[str, Any]:
        """
        Fetch latest national indicators from Layer 2
        
        Returns:
            Dict with structure:
            {
                "timestamp": "2025-12-14T08:00:00Z",
                "indicators": [
                    {
                        "indicator_code": "POL_UNREST_01",
                        "indicator_name": "Political Unrest Index",
                        "pestel_category": "Political",
                        "current_value": 78.5,
                        "normalized_value": 0.785,
                        "trend": {"direction": "rising", "strength": 0.82},
                        "confidence": 0.85
                    },
                    ...
                ]
            }
        """
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get latest indicator values (most recent for each indicator)
            cursor.execute("""
                SELECT DISTINCT ON (indicator_id)
                    indicator_id,
                    value,
                    confidence,
                    timestamp,
                    raw_count,
                    source_count,
                    extra_metadata
                FROM indicator_values
                ORDER BY indicator_id, timestamp DESC
            """)
            
            indicator_values = cursor.fetchall()

            # Get indicator metadata from MongoDB
            mongo_client = MongoClient(self.mongo_uri)
            db = mongo_client[self.mongo_db]

            # ---- Fix N+1: bulk-load latest calculation per indicator_id in ONE pass.
            # Layer 2 stores `calculation_timestamp` (NOT `timestamp`) per the blueprint.
            indicator_ids = [iv['indicator_id'] for iv in indicator_values]
            calc_by_id: Dict[str, Dict[str, Any]] = {}
            if indicator_ids:
                pipeline = [
                    {"$match": {"indicator_id": {"$in": indicator_ids}}},
                    {"$sort": {"calculation_timestamp": -1}},
                    {"$group": {"_id": "$indicator_id", "doc": {"$first": "$$ROOT"}}},
                ]
                for row in db.indicator_calculations.aggregate(pipeline):
                    calc_by_id[row["_id"]] = row["doc"]

            # Build indicators list
            indicators = []

            for iv in indicator_values:
                metadata = iv.get('extra_metadata', {}) or {}
                pestel_category = metadata.get('pestel_category', 'Economic')
                subcategory = metadata.get('subcategory', 'General')

                calc = calc_by_id.get(iv['indicator_id'])

                indicator_code = self._generate_indicator_code(pestel_category, subcategory)

                # Normalization respects the indicator's actual range when known.
                # Sentiment indicators are -1..1; frequency/index typically 0..100.
                raw_value = float(iv['value'])
                value_range = metadata.get('value_range')  # e.g. {"min": -1, "max": 1}
                if value_range and 'min' in value_range and 'max' in value_range:
                    vmin = float(value_range['min'])
                    vmax = float(value_range['max'])
                    span = vmax - vmin if vmax != vmin else 1.0
                    normalized = max(0.0, min(1.0, (raw_value - vmin) / span))
                else:
                    # Default: treat as 0-100 scale, but clamp instead of dividing blindly
                    normalized = max(0.0, min(1.0, raw_value / 100.0))

                indicator = {
                    'indicator_code': indicator_code,
                    'indicator_id': iv['indicator_id'],
                    'indicator_name': (calc.get('indicator_name', 'Unknown') if calc else 'Unknown'),
                    'pestel_category': pestel_category,
                    'subcategory': subcategory,
                    'current_value': raw_value,
                    'normalized_value': normalized,
                    'confidence': float(iv['confidence']),
                    'article_count': iv.get('raw_count', 0),
                    'source_count': iv.get('source_count', 0),
                    'timestamp': iv['timestamp'].isoformat(),
                }

                if calc and 'trend' in calc:
                    indicator['trend'] = calc['trend']
                if calc and 'geographic_distribution' in calc:
                    indicator['geographic_distribution'] = calc['geographic_distribution']

                indicators.append(indicator)
            
            cursor.close()
            conn.close()
            mongo_client.close()
            
            result = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'indicators': indicators,
                'total_count': len(indicators)
            }
            
            logger.info(f"Fetched {len(indicators)} national indicators from Layer 2")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Layer 2 indicators: {e}")
            raise
    
    def get_indicator_history(
        self,
        indicator_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical values for a specific indicator
        
        Args:
            indicator_id: The indicator to fetch
            days: Number of days of history
        
        Returns:
            List of {timestamp, value} dicts
        """
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # psycopg2 does NOT bind %s inside string literals.
            # INTERVAL must be built with a sanitized integer instead.
            days_int = max(0, int(days))
            cursor.execute(
                f"""
                SELECT timestamp, value
                FROM indicator_values
                WHERE indicator_id = %s
                  AND timestamp >= NOW() - INTERVAL '{days_int} days'
                ORDER BY timestamp ASC
                """,
                (indicator_id,),
            )
            
            history = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [
                {
                    'timestamp': row['timestamp'].isoformat(),
                    'value': float(row['value'])
                }
                for row in history
            ]
            
        except Exception as e:
            logger.error(f"Error fetching indicator history: {e}")
            return []
    
    def get_geographic_distribution(
        self,
        indicator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get geographic distribution of indicators
        
        Args:
            indicator_id: Optional specific indicator, or all if None
        
        Returns:
            Dict mapping locations to indicator values
        """
        try:
            mongo_client = MongoClient(self.mongo_uri)
            db = mongo_client[self.mongo_db]
            
            query = {}
            if indicator_id:
                query['indicator_id'] = indicator_id
            
            # Get latest calculations with geographic data
            calculations = db.indicator_calculations.find(
                query,
                {'indicator_id': 1, 'geographic_distribution': 1}
            ).sort('calculation_timestamp', -1).limit(100)
            
            geo_data = {}
            for calc in calculations:
                if 'geographic_distribution' in calc:
                    indicator_id = calc['indicator_id']
                    geo_data[indicator_id] = calc['geographic_distribution']
            
            mongo_client.close()
            return geo_data
            
        except Exception as e:
            logger.error(f"Error fetching geographic distribution: {e}")
            return {}
    
    def _generate_indicator_code(
        self,
        pestel_category: str,
        subcategory: str
    ) -> str:
        """
        Generate indicator code from category and subcategory
        
        Examples:
            Political, Civil Unrest -> POL_UNREST_01
            Economic, Fuel Availability -> ECON_FUEL_AVAIL
        """
        # Map PESTEL categories to prefixes
        category_prefixes = {
            'Political': 'POL',
            'Economic': 'ECON',
            'Social': 'SOCIAL',
            'Technological': 'TECH',
            'Environmental': 'ENV',
            'Legal': 'LEGAL'
        }
        
        prefix = category_prefixes.get(pestel_category, 'MISC')
        
        # Clean subcategory for code
        subcat_code = subcategory.replace(' ', '_').replace('-', '_').upper()
        
        # Truncate if too long
        if len(subcat_code) > 20:
            subcat_code = subcat_code[:20]
        
        return f"{prefix}_{subcat_code}"
    
    def test_connection(self) -> bool:
        """
        Test if connections to Layer 2 databases work
        
        Returns:
            True if both PostgreSQL and MongoDB are accessible
        """
        try:
            # Test PostgreSQL
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            conn.close()
            logger.info("✅ PostgreSQL connection successful")
            
            # Test MongoDB
            mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            mongo_client.server_info()  # Will raise exception if can't connect
            mongo_client.close()
            logger.info("✅ MongoDB connection successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


# Convenience function for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    connector = Layer2Connector()
    
    # Test connection
    if connector.test_connection():
        print("\n✅ Database connections working\n")
        
        # Fetch indicators
        indicators = connector.get_latest_national_indicators()
        print(f"📊 Fetched {indicators['total_count']} indicators")
        
        if indicators['indicators']:
            sample = indicators['indicators'][0]
            print(f"\nSample indicator:")
            print(f"  Code: {sample['indicator_code']}")
            print(f"  Name: {sample['indicator_name']}")
            print(f"  Value: {sample['current_value']}")
            print(f"  Confidence: {sample['confidence']}")
    else:
        print("\n❌ Database connection failed")
