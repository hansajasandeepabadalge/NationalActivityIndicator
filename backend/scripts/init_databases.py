"""
Database Initialization and Testing Script
Tests connections to all databases and initializes them if needed
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.mongodb_sync import mongodb_sync
from app.db.redis_sync import redis_cache_sync
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_postgresql():
    """Test PostgreSQL/TimescaleDB connection"""
    try:
        logger.info("Testing PostgreSQL/TimescaleDB connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ PostgreSQL connected: {version[:50]}...")

            # Check if TimescaleDB is enabled
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'timescaledb'"))
            if result.fetchone():
                logger.info("✅ TimescaleDB extension is enabled")
            else:
                logger.warning("⚠️  TimescaleDB extension not found")

            # Check if ENUM types exist
            result = conn.execute(text("""
                SELECT typname FROM pg_type
                WHERE typname IN ('pestel_category_enum', 'calculation_type_enum', 'event_type_enum', 'trend_direction_enum')
            """))
            enums = [row[0] for row in result]
            logger.info(f"✅ Found ENUM types: {', '.join(enums) if enums else 'None (will be created by migration)'}")

            return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False


def test_mongodb():
    """Test MongoDB connection"""
    try:
        logger.info("Testing MongoDB connection...")
        mongodb_sync.connect()
        db = mongodb_sync.get_database()

        # Test ping
        db.command("ping")
        logger.info("✅ MongoDB connected successfully")

        # List collections
        collections = db.list_collection_names()
        logger.info(f"✅ Found {len(collections)} collections: {', '.join(collections[:5])}")

        # Create indexes for Layer 2 collections if they don't exist
        logger.info("Creating MongoDB indexes...")

        # Indicator calculations
        indicator_calc = mongodb_sync.get_indicator_calculations()
        indicator_calc.create_index("indicator_id")
        indicator_calc.create_index("timestamp")

        # Entity extractions
        entity_extract = mongodb_sync.get_entity_extractions()
        entity_extract.create_index("article_id")
        entity_extract.create_index("extracted_at")

        logger.info("✅ MongoDB indexes created")

        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False
    finally:
        mongodb_sync.close()


def test_redis():
    """Test Redis connection"""
    try:
        logger.info("Testing Redis connection...")
        redis_cache_sync.connect()
        client = redis_cache_sync.get_client()

        # Test ping
        client.ping()
        logger.info("✅ Redis connected successfully")

        # Test set/get
        test_key = "test:connection"
        redis_cache_sync.set(test_key, {"test": "value"}, ttl=10)
        value = redis_cache_sync.get(test_key)
        if value and value.get("test") == "value":
            logger.info("✅ Redis read/write test passed")
        else:
            logger.warning("⚠️  Redis read/write test failed")

        # Clean up
        redis_cache_sync.delete(test_key)

        # Get Redis info
        info = client.info("server")
        logger.info(f"✅ Redis version: {info.get('redis_version', 'unknown')}")

        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False
    finally:
        redis_cache_sync.close()


def check_migrations():
    """Check if Alembic migrations have been run"""
    try:
        logger.info("Checking Alembic migration status...")
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'alembic_version'
                )
            """))
            exists = result.fetchone()[0]

            if exists:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.fetchone()
                if version:
                    logger.info(f"✅ Migrations applied: version {version[0]}")
                    return True
                else:
                    logger.warning("⚠️  Alembic version table exists but no version found")
                    return False
            else:
                logger.warning("⚠️  Migrations not yet applied. Run: alembic upgrade head")
                return False
    except Exception as e:
        logger.error(f"❌ Error checking migrations: {e}")
        return False


def check_tables():
    """Check if expected tables exist"""
    try:
        logger.info("Checking for Layer 2 tables...")
        expected_tables = [
            'indicator_definitions',
            'indicator_keywords',
            'indicator_values',
            'indicator_events',
            'indicator_correlations',
            'ml_classification_results',
            'trend_analysis'
        ]

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            existing_tables = [row[0] for row in result]

            found = []
            missing = []
            for table in expected_tables:
                if table in existing_tables:
                    found.append(table)
                else:
                    missing.append(table)

            if found:
                logger.info(f"✅ Found tables: {', '.join(found)}")
            if missing:
                logger.warning(f"⚠️  Missing tables: {', '.join(missing)}")

            return len(missing) == 0
    except Exception as e:
        logger.error(f"❌ Error checking tables: {e}")
        return False


def main():
    """Run all database tests"""
    logger.info("=" * 80)
    logger.info("DATABASE INITIALIZATION AND TESTING")
    logger.info("=" * 80)

    results = {
        "PostgreSQL": test_postgresql(),
        "MongoDB": test_mongodb(),
        "Redis": test_redis(),
        "Migrations": check_migrations(),
        "Tables": check_tables()
    }

    logger.info("=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)

    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {name}: {'PASSED' if status else 'FAILED'}")

    all_passed = all(results.values())

    if all_passed:
        logger.info("=" * 80)
        logger.info("🎉 ALL TESTS PASSED! Databases are ready.")
        logger.info("=" * 80)
        return 0
    else:
        logger.info("=" * 80)
        logger.info("⚠️  SOME TESTS FAILED. Please review the errors above.")
        logger.info("=" * 80)

        # Provide helpful instructions
        if not results["Migrations"]:
            logger.info("\n💡 To apply migrations, run:")
            logger.info("   cd backend")
            logger.info("   alembic upgrade head")

        if not results["PostgreSQL"]:
            logger.info("\n💡 To start PostgreSQL, run:")
            logger.info("   cd backend")
            logger.info("   docker-compose up -d timescaledb")

        if not results["MongoDB"]:
            logger.info("\n💡 To start MongoDB, run:")
            logger.info("   cd backend")
            logger.info("   docker-compose up -d mongodb")

        if not results["Redis"]:
            logger.info("\n💡 To start Redis, run:")
            logger.info("   cd backend")
            logger.info("   docker-compose up -d redis")

        return 1


if __name__ == "__main__":
    exit(main())
