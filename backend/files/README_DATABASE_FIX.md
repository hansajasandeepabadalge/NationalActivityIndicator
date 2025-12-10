# PostgreSQL Authentication Fix for Windows-Docker

## Problem
PostgreSQL authentication fails from Windows host with:
```
FATAL: password authentication failed for user "postgres"
```

## Root Cause
- Windows → Docker network bridge has issues with PostgreSQL SCRAM-SHA-256 authentication
- Environment variable `POSTGRES_PASSWORD` doesn't always initialize properly in TimescaleDB container
- This happens EVERY time you recreate Docker volumes

## Permanent Solution

### Option 1: Run Python Scripts Inside Docker (RECOMMENDED)
Instead of running scripts from Windows, run them inside a Docker container:

```bash
# Run ANY Python script inside Docker network:
docker run --rm \
  --network backend_indicator_network \
  -v "$(pwd):/app" \
  -w /app \
  python:3.12-slim \
  bash -c "pip install -q psycopg2-binary && python your_script.py"
```

**Connection string in scripts:** Use Docker service name:
```python
DATABASE_URL = "postgresql://postgres:postgres_secure_2024@national_indicator_timescaledb:5432/national_indicator"
```

### Option 2: Use pgAdmin (Web UI)
1. Open http://localhost:5050
2. Login: `admin@indicator.local` / `admin_secure_2024`
3. Add server:
   - Host: `national_indicator_timescaledb`
   - Port: `5432`
   - User: `postgres`
   - Password: `postgres_secure_2024`

### Option 3: One-Time Manual Fix
If you MUST connect from Windows:

```bash
# 1. Fix pg_hba.conf (change to MD5)
docker exec national_indicator_timescaledb sh -c "sed -i 's/scram-sha-256/md5/g' /var/lib/postgresql/data/pg_hba.conf"

# 2. Set password
docker exec national_indicator_timescaledb psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'postgres_secure_2024';"

# 3. Reload config
docker exec national_indicator_timescaledb psql -U postgres -c "SELECT pg_reload_conf();"

# 4. Restart container
docker restart national_indicator_timescaledb

# 5. Test (wait 10 seconds first)
sleep 10
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:postgres_secure_2024@127.0.0.1:5432/national_indicator'); print('OK'); conn.close()"
```

**NOTE:** This fix is TEMPORARY and will be lost if you recreate the Docker volume.

## Best Practice for Layer 2 Development

Create a wrapper script to run Day 2 tests inside Docker:

```bash
# backend/run_test_in_docker.sh
docker run --rm \
  --network backend_indicator_network \
  -v "$(pwd):/app" \
  -w /app \
  python:3.12-slim \
  bash -c "
    pip install -q psycopg2-binary pydantic sqlalchemy &&
    python tests/integration/test_classification_pipeline.py
  "
```

## Why This Works
- Docker containers on the same network can communicate directly using service names
- No Windows network stack issues
- No authentication translation problems
- Consistent and reliable

## Quick Reference
```bash
# From Windows (unreliable):
❌ postgresql://postgres:password@127.0.0.1:5432/db

# From Docker container (reliable):
✅ postgresql://postgres:password@national_indicator_timescaledb:5432/db
```
