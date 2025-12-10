# Layer 2 Setup Guide

## Overview

This guide helps you set up the complete Layer 2 environment for the National Activity Indicator System.

## Prerequisites

1. **Docker Desktop** - Running and accessible
2. **Python 3.10+** - Installed and in PATH
3. **Git** - For version control

## Quick Start (Automated)

### Windows:
```bash
cd backend
scripts\setup_layer2.bat
```

### Linux/Mac:
```bash
cd backend
bash scripts/setup_layer2.sh
```

This will automatically:
- Start all Docker containers (PostgreSQL/TimescaleDB, MongoDB, Redis)
- Install Python dependencies
- Download ML models (spaCy)
- Run database migrations
- Verify all connections

## Manual Setup

If you prefer to set up step by step:

### Step 1: Start Docker Containers

```bash
cd backend
docker-compose up -d
```

This starts:
- **TimescaleDB** (PostgreSQL with time-series extension) - Port 5432
- **MongoDB** - Port 27017
- **Redis** - Port 6379
- **pgAdmin** (Database UI) - Port 5050
- **Mongo Express** (MongoDB UI) - Port 8081
- **Redis Commander** (Redis UI) - Port 8082

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Download ML Models

```bash
python -m spacy download en_core_web_sm
```

### Step 4: Run Database Migrations

```bash
alembic upgrade head
```

This creates all required tables and TimescaleDB hypertables.

### Step 5: Verify Setup

```bash
python scripts/init_databases.py
```

This tests all database connections and verifies the setup.

## Starting the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## Database Access

### PostgreSQL/TimescaleDB

**Connection String:**
```
postgresql://postgres:postgres_secure_2024@localhost:5432/national_indicator
```

**pgAdmin UI:**
- URL: http://localhost:5050
- Email: admin@indicator.local
- Password: admin_secure_2024

### MongoDB

**Connection String:**
```
mongodb://admin:mongo_secure_2024@localhost:27017/national_indicator?authSource=admin
```

**Mongo Express UI:**
- URL: http://localhost:8081
- Username: admin
- Password: admin

### Redis

**Connection String:**
```
redis://localhost:6379/0
```

**Redis Commander UI:**
- URL: http://localhost:8082

## Environment Variables

All configuration is in `.env` file. Key variables:

```env
# Database passwords
POSTGRES_PASSWORD=postgres_secure_2024
MONGO_PASSWORD=mongo_secure_2024

# Database URLs
DATABASE_URL=postgresql://postgres:postgres_secure_2024@localhost:5432/national_indicator
MONGODB_URL=mongodb://admin:mongo_secure_2024@localhost:27017/national_indicator?authSource=admin
REDIS_URL=redis://localhost:6379/0

# Application
PROJECT_NAME=National Activity Indicator
DEBUG=True
```

## Common Issues & Solutions

### Issue: Docker containers won't start

**Solution:**
1. Ensure Docker Desktop is running
2. Check if ports are already in use:
   ```bash
   netstat -an | findstr "5432 27017 6379"
   ```
3. Stop conflicting services or change ports in docker-compose.yml

### Issue: Database connection errors

**Solution:**
1. Wait 30 seconds for databases to fully initialize
2. Check container status: `docker-compose ps`
3. View logs: `docker-compose logs timescaledb` (or mongodb/redis)

### Issue: Alembic migration fails

**Solution:**
1. Ensure TimescaleDB container is fully started
2. Check if init_timescale.sql ran: `docker-compose logs timescaledb | grep "CREATE EXTENSION"`
3. Reset and retry:
   ```bash
   docker-compose down -v
   docker-compose up -d
   # Wait 30 seconds
   alembic upgrade head
   ```

### Issue: Python dependencies fail to install

**Solution:**
1. Upgrade pip: `pip install --upgrade pip`
2. Install build tools (Windows): Install Visual Studio Build Tools
3. Install build tools (Linux): `sudo apt-get install python3-dev build-essential`

### Issue: spaCy model download fails

**Solution:**
1. Manual download:
   ```bash
   pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
   ```

## Database Schema

### TimescaleDB Tables:
- `indicator_definitions` - Indicator metadata
- `indicator_keywords` - Keywords for classification
- `indicator_values` - Time-series indicator values (hypertable)
- `indicator_events` - Time-series events (hypertable)
- `indicator_correlations` - Correlation analysis
- `ml_classification_results` - ML predictions
- `trend_analysis` - Trend analysis results

### MongoDB Collections:
- `indicator_calculations` - Detailed calculation breakdowns
- `indicator_narratives` - Generated narratives
- `entity_extractions` - Extracted entities from articles
- `ml_training_data` - Training data for ML models
- `raw_articles` - Raw article data
- `processed_content` - Processed article data

### Redis Keys:
- `indicator:current:{id}` - Current indicator values
- `ml:prediction:{article_id}` - ML predictions
- `trend:analysis:{id}` - Trend analysis cache

## Stopping the System

### Stop application only:
```bash
Ctrl+C  (in uvicorn terminal)
```

### Stop Docker containers:
```bash
docker-compose stop
```

### Stop and remove all data:
```bash
docker-compose down -v
```

**⚠️ Warning:** `-v` flag deletes all database data!

## Next Steps

After successful setup:

1. **Review Documentation**: Check `LAYER2_TASK_DISTRIBUTION.md` for development tasks
2. **Populate Indicators**: Run indicator definition scripts
3. **Test APIs**: Use http://localhost:8000/api/docs
4. **Start Development**: Follow Day 2-7 tasks in task distribution

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify connections: `python scripts/init_databases.py`
3. Review this guide's troubleshooting section
