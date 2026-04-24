# Manual Steps Required After Automatic Fixes

## ✅ What Has Been Fixed Automatically

All code issues have been fixed:
1. ✅ Created FastAPI application with database lifecycle management
2. ✅ Fixed Alembic migration to create ENUMs properly
3. ✅ Created sync database wrappers for MongoDB and Redis
4. ✅ Updated requirements.txt with missing dependencies
5. ✅ Fixed docker-compose.yml initialization order
6. ✅ Updated Alembic env.py configuration
7. ✅ Created database initialization and testing scripts
8. ✅ Created automated setup scripts (Windows & Linux)
9. ✅ Created comprehensive setup documentation

## ⚠️ Manual Steps YOU Need to Do

### Step 1: Install Python Dependencies ⭐ REQUIRED

You need to install/update Python packages:

```bash
cd backend
pip install -r requirements.txt
```

**What this does:**
- Installs FastAPI with latest version
- Installs Redis with async support (`redis[asyncio]`)
- Installs `hiredis` for better Redis performance
- Updates all other dependencies

**Estimated time:** 2-5 minutes

---

### Step 2: Restart Docker Containers ⭐ REQUIRED

The docker-compose.yml was updated, so restart containers:

```bash
cd backend
docker-compose down
docker-compose up -d
```

**What this does:**
- Stops existing containers
- Starts fresh containers with updated configuration
- TimescaleDB init script will run with proper naming

**Estimated time:** 1-2 minutes

---

### Step 3: Run Database Migrations ⭐ REQUIRED

Apply the fixed Alembic migration:

```bash
cd backend
alembic upgrade head
```

**What this does:**
- Creates all ENUM types properly
- Creates all tables (indicator_definitions, indicator_values, etc.)
- Converts tables to TimescaleDB hypertables
- Creates indexes for performance

**Estimated time:** 30 seconds

**If this fails:**
- Make sure Docker containers are running: `docker-compose ps`
- Check if databases are ready: `python scripts/init_databases.py`
- If still fails, reset database:
  ```bash
  docker-compose down -v
  docker-compose up -d
  # Wait 30 seconds
  alembic upgrade head
  ```

---

### Step 4: Download spaCy Model (Optional but Recommended)

For NLP processing, download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

**What this does:**
- Downloads spaCy's English language model
- Required for entity extraction and NLP tasks

**Estimated time:** 1-2 minutes

**Can skip if:** You're not using NLP features yet

---

### Step 5: Verify Setup ⭐ REQUIRED

Test all database connections:

```bash
cd backend
python scripts/init_databases.py
```

**What this does:**
- Tests PostgreSQL/TimescaleDB connection
- Tests MongoDB connection
- Tests Redis connection
- Checks if migrations ran successfully
- Verifies all tables exist
- Creates MongoDB indexes

**Expected output:**
```
✅ PostgreSQL: PASSED
✅ MongoDB: PASSED
✅ Redis: PASSED
✅ Migrations: PASSED
✅ Tables: PASSED
🎉 ALL TESTS PASSED! Databases are ready.
```

**Estimated time:** 10-20 seconds

---

### Step 6: Start the Application (Optional - To Test)

Start the FastAPI server to verify everything works:

```bash
cd backend
uvicorn app.main:app --reload
```

**What this does:**
- Starts FastAPI application
- Connects to all databases on startup
- Provides API endpoints

**Access:**
- API Docs: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health
- Detailed Health: http://localhost:8000/health/detailed

**Expected startup logs:**
```
Connecting to MongoDB...
✅ MongoDB connected successfully
Connecting to Redis...
✅ Redis connected successfully
🚀 Application startup complete
```

**Can skip if:** You just want to verify setup for now

---

## 🚀 Quick Setup (All Steps Combined)

If you want to run everything at once:

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

This automated script runs all steps 1-5 for you!

---

## ❌ Things You Do NOT Need to Do

✅ **No manual database account creation** - All accounts are created automatically via docker-compose
✅ **No manual database configuration** - Everything is in .env file
✅ **No manual schema creation** - Alembic migrations handle this
✅ **No version updates needed** - All versions are already specified in requirements.txt
✅ **No code changes needed** - All fixes have been applied

---

## 🔑 Database Credentials (Already Configured)

All credentials are in the `.env` file and already configured:

### PostgreSQL/TimescaleDB:
- Host: localhost
- Port: 5432
- Database: national_indicator
- Username: postgres
- Password: postgres_secure_2024

### MongoDB:
- Host: localhost
- Port: 27017
- Database: national_indicator
- Username: admin
- Password: mongo_secure_2024

### Redis:
- Host: localhost
- Port: 6379
- Database: 0
- Password: (none)

---

## 🎯 Summary: What You MUST Do

### Minimum Required Steps:

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Restart Docker**: `docker-compose down && docker-compose up -d`
3. **Run migrations**: `alembic upgrade head`
4. **Verify setup**: `python scripts/init_databases.py`

**Total estimated time: 5-10 minutes**

### Optional Steps:

5. Download spaCy model: `python -m spacy download en_core_web_sm`
6. Start application: `uvicorn app.main:app --reload`

---

## 🆘 If Something Goes Wrong

### All tests pass except migrations:
```bash
# Reset database and retry
docker-compose down -v
docker-compose up -d
sleep 30  # Wait for databases
alembic upgrade head
```

### Docker containers won't start:
1. Make sure Docker Desktop is running
2. Check for port conflicts: `netstat -an | findstr "5432 27017 6379"`
3. Check logs: `docker-compose logs`

### Python package installation fails:
1. Upgrade pip: `pip install --upgrade pip`
2. Try with admin/sudo if permission error
3. Create virtual environment if not using one

### Can't connect to databases:
1. Wait 30-60 seconds after `docker-compose up`
2. Check container status: `docker-compose ps`
3. Verify ports are not blocked by firewall

---

## 📚 Additional Resources

- **Detailed Setup Guide**: `backend/LAYER2_SETUP.md`
- **Task Distribution**: `LAYER2_TASK_DISTRIBUTION.md`
- **System Blueprint**: `SYSTEM_BLUEPRINT.md`

---

## ✅ Checklist

Use this to track your progress:

- [ ] Step 1: Installed Python dependencies
- [ ] Step 2: Restarted Docker containers
- [ ] Step 3: Ran Alembic migrations
- [ ] Step 4: Downloaded spaCy model (optional)
- [ ] Step 5: Verified setup (all tests passed)
- [ ] Step 6: Started application and tested (optional)

---

**Once all required steps are complete, your Layer 2 environment is fully operational!**
