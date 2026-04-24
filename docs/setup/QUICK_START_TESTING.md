# 🚀 Quick Start Guide - Local Testing

## ✅ Prerequisites (Already Done)
- PostgreSQL running on port 5432
- MongoDB running on port 27017
- Redis running on port 6379
- Backend running on port 8080
- Frontend running on port 3000

---

## 📋 Step-by-Step Testing Guide

### **Step 1: Set Up API Keys**

1. **Get FREE Groq API Key:**
   - Visit: https://console.groq.com/
   - Sign up (free)
   - Create an API key
   - Copy the key

2. **Create `.env` file:**
   ```powershell
   cd backend
   cp .env.example .env
   ```

3. **Edit `.env` file:**
   - Open `backend/.env` in your editor
   - Replace `your_groq_api_key_here` with your actual Groq API key
   - Save the file

4. **Restart backend:**
   ```powershell
   # Stop current backend (Ctrl+C)
   # Then restart:
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

---

### **Step 2: Trigger First Data Collection**

**Option A: Using PowerShell**
```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8080/api/v1/agents/cycle/start"
```

**Option B: Using Python Script**
```powershell
cd backend
python -c "import asyncio; from app.orchestrator import create_orchestrator; asyncio.run(create_orchestrator().run_cycle())"
```

**Option C: Via Swagger UI**
- Open: http://localhost:8080/api/v1/docs
- Find `/agents/cycle/start` endpoint
- Click "Try it out" → "Execute"

---

### **Step 3: Monitor Progress**

**Check Scraping Status:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/agents/status"
```

**Check Data Collection:**
```powershell
cd backend
python -c "from pymongo import MongoClient; c = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'); print('Articles:', c.national_indicator.raw_articles.count_documents({})); print('Indicators:', c.national_indicator.indicator_calculations.count_documents({}))"
```

---

### **Step 4: View Dashboard**

1. **Login to Dashboard:**
   - Open: http://localhost:3000/login
   - Email: `admin@example.com`
   - Password: `admin123`

2. **Navigate to Dashboard:**
   - Click "Dashboard" or go to: http://localhost:3000/dashboard
   - You should now see indicators and data!

---

## 🔄 Running Regular Data Updates

**For continuous testing, run cycles periodically:**

```powershell
# Every 30 minutes (example)
while ($true) {
    Write-Host "Starting data collection cycle..." -ForegroundColor Green
    Invoke-RestMethod -Method POST -Uri "http://localhost:8080/api/v1/agents/cycle/start"
    Write-Host "Cycle complete. Waiting 30 minutes..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1800
}
```

---

## 📊 Verify Data Flow

**Check each layer has data:**

```powershell
cd backend

# Layer 1 - Raw articles
python -c "from pymongo import MongoClient; c = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'); print('Layer 1 - Raw articles:', c.national_indicator.raw_articles.count_documents({}))"

# Layer 2 - National indicators
python -c "from app.core.config import settings; from sqlalchemy import create_engine, text; e = create_engine(settings.DATABASE_URL); c = e.connect(); print('Layer 2 - Indicators:', c.execute(text('SELECT COUNT(*) FROM indicator_values')).scalar())"

# Layer 4 - Business insights
python -c "from app.core.config import settings; from sqlalchemy import create_engine, text; e = create_engine(settings.DATABASE_URL); c = e.connect(); print('Layer 4 - Insights:', c.execute(text('SELECT COUNT(*) FROM business_insights')).scalar())"
```

---

## 🐛 Troubleshooting

### **Dashboard shows no data:**
- Wait 2-3 minutes after triggering scraping cycle
- Check backend logs for errors
- Verify Groq API key is set correctly
- Try running cycle again

### **Scraping fails:**
- Check internet connection
- Some news sites might block scrapers (expected)
- Check backend logs: look for "SUCCESS" messages

### **Backend errors:**
- Check all databases are running (PostgreSQL, MongoDB, Redis)
- Verify `.env` file has correct credentials
- Check port 8080 is not in use by another app

---

## 🚀 When Ready for Production

**After testing is complete, deploy to cloud:**

1. **Choose a cloud provider:**
   - AWS (EC2, RDS, DocumentDB)
   - DigitalOcean (Droplets + Managed Databases)
   - Azure (VMs + Cosmos DB)
   - Heroku (easiest but more expensive)

2. **Use Docker for deployment:**
   ```bash
   docker-compose up -d
   ```

3. **Set up automated scheduling:**
   - Use cron jobs (Linux) or Task Scheduler (Windows Server)
   - Or use Celery + Redis for background tasks

4. **Configure domain and SSL:**
   - Get domain name
   - Set up HTTPS with Let's Encrypt
   - Configure CORS for your domain

5. **Change security settings:**
   - Generate new SECRET_KEY
   - Use strong database passwords
   - Enable authentication on all databases
   - Set DEBUG=false

---

## 📝 Notes for Local Testing

- **Cost:** FREE (except Groq API - free tier generous)
- **Data persistence:** Data stays on your PC
- **Uptime:** Only when your PC is running
- **Perfect for:** Development, testing, demos
- **Not suitable for:** 24/7 production, multiple users

**When you see data in dashboard → System works! Ready for cloud deployment.**
