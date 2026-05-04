# Deployment Guide

## Quick Start (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Start databases
docker-compose up -d

# 3. Run migrations
alembic upgrade head

# 4. Start server
uvicorn app.main:app --reload

# Visit: http://localhost:8000
```

## Production Deployment

```bash
# 1. Configure environment
cp .env.template .env
# Edit .env with production values

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Check health
curl http://localhost:8000/health
```

## Monitoring

- **Health**: GET /health
- **API Docs**: GET /docs
- **Dashboard**: GET /

## Backup

```bash
# MongoDB
mongodump --uri="mongodb://admin:pass@host:27017/national_indicator"

# PostgreSQL
pg_dump -h localhost -U postgres national_indicator > backup.sql
```
