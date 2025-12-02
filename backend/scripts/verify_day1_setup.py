#!/usr/bin/env python3
"""
Day 1 Checkpoint Verification Script
Verifies all Day 1 setup tasks are complete
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_environment():
    """Verify .env file exists"""
    print("\n1. Checking environment configuration...")
    env_file = Path(__file__).parent.parent / ".env"
    env_example = Path(__file__).parent.parent / ".env.example"

    if not env_example.exists():
        print("   ❌ .env.example not found")
        return False

    if not env_file.exists():
        print("   ⚠️  .env file not found")
        print("   💡 Run: cp .env.example .env")
        return False

    print("   ✅ Environment configuration exists")
    return True

def verify_docker():
    """Verify Docker containers are running"""
    print("\n2. Checking Docker containers...")
    import subprocess

    try:
        result = subprocess.run(
            ["docker-compose", "ps"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print("   ❌ Docker Compose not running")
            print("   💡 Run: docker-compose up -d")
            return False

        # Check for expected services
        required_services = ['timescaledb', 'mongodb', 'redis']
        output = result.stdout

        for service in required_services:
            if service in output and 'Up' in output:
                print(f"   ✅ {service} is running")
            else:
                print(f"   ❌ {service} is not running")
                return False

        return True

    except FileNotFoundError:
        print("   ❌ Docker Compose not installed or not in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ Docker command timed out")
        return False

def verify_database_connections():
    """Verify all database connections"""
    print("\n3. Testing database connections...")

    try:
        from app.core.config import settings
        import psycopg2
        from pymongo import MongoClient
        import redis

        # Test PostgreSQL
        try:
            conn = psycopg2.connect(
                settings.DATABASE_URL.replace('postgresql://', 'postgresql://')
            )
            cur = conn.cursor()
            cur.execute("SELECT version();")
            cur.close()
            conn.close()
            print("   ✅ PostgreSQL/TimescaleDB connected")
        except Exception as e:
            print(f"   ❌ PostgreSQL connection failed: {e}")
            return False

        # Test MongoDB
        try:
            client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            client.close()
            print("   ✅ MongoDB connected")
        except Exception as e:
            print(f"   ❌ MongoDB connection failed: {e}")
            return False

        # Test Redis
        try:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            r.close()
            print("   ✅ Redis connected")
        except Exception as e:
            print(f"   ❌ Redis connection failed: {e}")
            return False

        return True

    except ImportError as e:
        print(f"   ❌ Missing dependencies: {e}")
        print("   💡 Run: pip install -r requirements.txt")
        return False

def verify_project_structure():
    """Verify Layer 2 directory structure"""
    print("\n4. Checking project structure...")

    base_path = Path(__file__).parent.parent / "app" / "layer2"
    required_dirs = [
        "data_ingestion",
        "nlp_processing",
        "indicator_calculation",
        "ml_classification",
        "trend_analysis",
        "correlation_analysis",
        "api",
        "utils"
    ]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ exists")
        else:
            print(f"   ❌ {dir_name}/ missing")
            all_exist = False

    return all_exist

def verify_models():
    """Verify SQLAlchemy models"""
    print("\n5. Checking SQLAlchemy models...")

    try:
        from app.models import (
            IndicatorDefinition,
            IndicatorKeyword,
            IndicatorValue,
            IndicatorEvent,
            IndicatorCorrelation,
            MLClassificationResult,
            TrendAnalysis
        )
        print("   ✅ All models imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Model import failed: {e}")
        return False

def verify_migrations():
    """Verify Alembic migrations"""
    print("\n6. Checking database migrations...")

    migrations_dir = Path(__file__).parent.parent / "alembic" / "versions"

    if not migrations_dir.exists():
        print("   ❌ Migrations directory not found")
        return False

    migration_files = list(migrations_dir.glob("*.py"))
    migration_files = [f for f in migration_files if f.name != "__init__.py"]

    if len(migration_files) == 0:
        print("   ❌ No migration files found")
        return False

    print(f"   ✅ Found {len(migration_files)} migration file(s)")

    # Check if migrations have been applied
    try:
        from app.core.config import settings
        import psycopg2

        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()

        # Check if alembic_version table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'alembic_version'
            );
        """)

        table_exists = cur.fetchone()[0]

        if table_exists:
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            if version:
                print(f"   ✅ Migrations applied (version: {version[0]})")
            else:
                print("   ⚠️  Alembic table exists but no version recorded")
                print("   💡 Run: alembic upgrade head")
                cur.close()
                conn.close()
                return False
        else:
            print("   ⚠️  Migrations not yet applied")
            print("   💡 Run: alembic upgrade head")
            cur.close()
            conn.close()
            return False

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"   ⚠️  Could not check migration status: {e}")
        return False

def verify_mock_data():
    """Verify mock data generated"""
    print("\n7. Checking mock data...")

    mock_file = Path(__file__).parent.parent / "data" / "mock" / "mock_articles.json"

    if not mock_file.exists():
        print("   ❌ Mock data file not found")
        print("   💡 Run: python scripts/generate_mock_data.py")
        return False

    import json
    with open(mock_file, 'r') as f:
        data = json.load(f)

    article_count = data['metadata']['total_articles']

    if article_count >= 200:
        print(f"   ✅ Mock data generated ({article_count} articles)")
        return True
    else:
        print(f"   ⚠️  Only {article_count} articles found (expected 200+)")
        return False

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("Day 1 Checkpoint Verification")
    print("=" * 70)

    checks = [
        ("Environment Configuration", verify_environment),
        ("Docker Containers", verify_docker),
        ("Database Connections", verify_database_connections),
        ("Project Structure", verify_project_structure),
        ("SQLAlchemy Models", verify_models),
        ("Database Migrations", verify_migrations),
        ("Mock Data", verify_mock_data),
    ]

    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n   ❌ Check failed with error: {e}")
            results[check_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check_name, passed_check in results.items():
        status = "✅ PASS" if passed_check else "❌ FAIL"
        print(f"{check_name:30} {status}")

    print("=" * 70)
    print(f"\nPassed: {passed}/{total} checks")

    if passed == total:
        print("\n🎉 Day 1 checkpoint complete! Ready for Day 2 development.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
