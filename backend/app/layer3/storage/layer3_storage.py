"""
Layer 3 Storage Layer

Handles all database writes for Layer 3 operational indicators
Stores to PostgreSQL (TimescaleDB) and MongoDB
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class Layer3Storage:
    """
    Persist Layer 3 operational indicators and calculations to databases
    """
    
    def __init__(self):
        """Initialize database connections"""
        # PostgreSQL connection (TimescaleDB)
        self.pg_config = {
            'host': '127.0.0.1',
            'port': 15432,
            'database': 'national_indicator',
            'user': 'postgres',
            'password': 'postgres_secure_2024'
        }
        
        # MongoDB connection
        self.mongo_uri = 'mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'
        self.mongo_db = 'national_indicator'
        
        logger.info("Layer3Storage initialized")
    
    async def store_operational_indicators(
        self,
        company_id: str,
        indicators: Dict[str, float],
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store operational indicator values to TimescaleDB
        
        Args:
            company_id: Company identifier
            indicators: Dict of {indicator_code: value}
            timestamp: Optional timestamp (defaults to now)
            metadata: Optional additional metadata
        
        Returns:
            Number of indicators stored
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Prepare data for batch insert
            values = []
            for indicator_code, value in indicators.items():
                values.append((
                    company_id,
                    indicator_code,
                    timestamp,
                    value,
                    metadata.get('confidence', 0.8) if metadata else 0.8,
                    metadata.get('calculation_method', 'calculated') if metadata else 'calculated',
                    metadata.get('source_indicators', []) if metadata else [],
                    metadata if metadata else {}
                ))
            
            # Batch insert
            execute_values(
                cursor,
                """
                INSERT INTO operational_indicator_values 
                (company_id, indicator_code, timestamp, value, confidence, 
                 calculation_method, source_indicators, metadata)
                VALUES %s
                ON CONFLICT (company_id, indicator_code, timestamp) 
                DO UPDATE SET 
                    value = EXCLUDED.value,
                    confidence = EXCLUDED.confidence,
                    metadata = EXCLUDED.metadata
                """,
                values
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Stored {len(indicators)} operational indicators for {company_id}")
            return len(indicators)
            
        except Exception as e:
            logger.error(f"Error storing operational indicators: {e}")
            raise
    
    async def store_calculation_details(
        self,
        company_id: str,
        calculation_data: Dict[str, Any]
    ) -> str:
        """
        Store detailed calculation results to MongoDB
        
        Args:
            company_id: Company identifier
            calculation_data: Full calculation details
        
        Returns:
            MongoDB document ID
        """
        try:
            mongo_client = MongoClient(self.mongo_uri)
            db = mongo_client[self.mongo_db]
            
            # Add metadata
            calculation_data['company_id'] = company_id
            calculation_data['timestamp'] = datetime.now()
            calculation_data['stored_at'] = datetime.now()
            
            # Insert to operational_calculations collection
            result = db.operational_calculations.insert_one(calculation_data)
            
            mongo_client.close()
            
            logger.info(f"Stored calculation details for {company_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing calculation details: {e}")
            raise
    
    async def store_company_snapshot(
        self,
        company_id: str,
        snapshot: Dict[str, Any]
    ) -> str:
        """
        Store point-in-time company operational state
        
        Args:
            company_id: Company identifier
            snapshot: Complete operational state snapshot
        
        Returns:
            MongoDB document ID
        """
        try:
            mongo_client = MongoClient(self.mongo_uri)
            db = mongo_client[self.mongo_db]
            
            # Add metadata
            snapshot['company_id'] = company_id
            snapshot['snapshot_time'] = datetime.now()
            
            # Insert to company_snapshots collection
            result = db.company_snapshots.insert_one(snapshot)
            
            mongo_client.close()
            
            logger.info(f"Stored company snapshot for {company_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing company snapshot: {e}")
            raise
    
    async def get_latest_indicators(
        self,
        company_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Retrieve latest operational indicators for a company
        
        Args:
            company_id: Company identifier
            limit: Maximum number of indicators to return
        
        Returns:
            Dict with indicators and metadata
        """
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Get latest value for each indicator
            cursor.execute("""
                SELECT DISTINCT ON (indicator_code)
                    indicator_code,
                    timestamp,
                    value,
                    confidence,
                    calculation_method,
                    metadata
                FROM operational_indicator_values
                WHERE company_id = %s
                ORDER BY indicator_code, timestamp DESC
                LIMIT %s
            """, (company_id, limit))
            
            rows = cursor.fetchall()
            
            indicators = {}
            for row in rows:
                indicators[row[0]] = {
                    'value': float(row[2]),
                    'timestamp': row[1].isoformat(),
                    'confidence': float(row[3]),
                    'calculation_method': row[4],
                    'metadata': row[5]
                }
            
            cursor.close()
            conn.close()
            
            return {
                'company_id': company_id,
                'indicators': indicators,
                'count': len(indicators)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving indicators: {e}")
            return {'company_id': company_id, 'indicators': {}, 'count': 0}
    
    async def get_latest_snapshot(
        self,
        company_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get most recent company snapshot from MongoDB
        
        Args:
            company_id: Company identifier
        
        Returns:
            Latest snapshot or None
        """
        try:
            mongo_client = MongoClient(self.mongo_uri)
            db = mongo_client[self.mongo_db]
            
            snapshot = db.company_snapshots.find_one(
                {'company_id': company_id},
                sort=[('snapshot_time', -1)]
            )
            
            mongo_client.close()
            
            if snapshot:
                # Convert ObjectId to string
                snapshot['_id'] = str(snapshot['_id'])
                if 'snapshot_time' in snapshot:
                    snapshot['snapshot_time'] = snapshot['snapshot_time'].isoformat()
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error retrieving snapshot: {e}")
            return None
    
    async def get_indicator_history(
        self,
        company_id: str,
        indicator_code: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get historical values for a specific operational indicator
        
        Args:
            company_id: Company identifier
            indicator_code: Indicator to fetch
            days: Number of days of history
        
        Returns:
            List of {timestamp, value} dicts
        """
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, value, confidence
                FROM operational_indicator_values
                WHERE company_id = %s
                  AND indicator_code = %s
                  AND timestamp >= NOW() - INTERVAL '%s days'
                ORDER BY timestamp ASC
            """, (company_id, indicator_code, days))
            
            rows = cursor.fetchall()
            
            history = [
                {
                    'timestamp': row[0].isoformat(),
                    'value': float(row[1]),
                    'confidence': float(row[2])
                }
                for row in rows
            ]
            
            cursor.close()
            conn.close()
            
            return history
            
        except Exception as e:
            logger.error(f"Error retrieving indicator history: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test if database connections work
        
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
            mongo_client.server_info()
            mongo_client.close()
            logger.info("✅ MongoDB connection successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False


# Convenience function for testing
if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    storage = Layer3Storage()
    
    # Test connection
    if storage.test_connection():
        print("\n✅ Database connections working\n")
        
        # Test storing indicators
        async def test_store():
            test_indicators = {
                'transport_availability': 75.5,
                'workforce_availability': 82.3,
                'supply_chain_integrity': 68.9,
                'cost_pressure': 45.2
            }
            
            count = await storage.store_operational_indicators(
                'test_retail_001',
                test_indicators,
                metadata={'confidence': 0.85, 'calculation_method': 'universal'}
            )
            print(f"✅ Stored {count} test indicators")
            
            # Retrieve them
            result = await storage.get_latest_indicators('test_retail_001', limit=10)
            print(f"✅ Retrieved {result['count']} indicators")
            for code, data in list(result['indicators'].items())[:3]:
                print(f"  {code}: {data['value']}")
        
        asyncio.run(test_store())
    else:
        print("\n❌ Database connection failed")
