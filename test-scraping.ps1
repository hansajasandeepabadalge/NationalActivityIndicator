# ============================================
# National Activity Indicator - Test Scraping Script
# ============================================
# This script triggers a scraping cycle and monitors the results

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "National Activity Indicator - Data Collection Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$BackendUrl = "http://localhost:8080/api/v1"
$MongoUrl = "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin"

# Step 1: Check if backend is running
Write-Host "[1/5] Checking backend status..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$BackendUrl/health" -ErrorAction Stop
    Write-Host "✓ Backend is running" -ForegroundColor Green
    Write-Host "  Status: $($healthCheck.status)" -ForegroundColor Gray
    Write-Host "  Database: $($healthCheck.database)" -ForegroundColor Gray
}
catch {
    Write-Host "✗ Backend is not responding on port 8080" -ForegroundColor Red
    Write-Host "  Please start backend first: cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload" -ForegroundColor Red
    exit 1
}

# Step 2: Check current data count
Write-Host "`n[2/5] Checking current data count..." -ForegroundColor Yellow
try {
    $beforeCount = python -c "from pymongo import MongoClient; c = MongoClient('$MongoUrl'); print(c.national_indicator.raw_articles.count_documents({}))"
    Write-Host "✓ Current articles in database: $beforeCount" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Could not check MongoDB (might not be running)" -ForegroundColor Yellow
}

# Step 3: Trigger scraping cycle
Write-Host "`n[3/5] Starting data collection cycle..." -ForegroundColor Yellow
Write-Host "  This may take 1-3 minutes..." -ForegroundColor Gray
try {
    $result = Invoke-RestMethod -Method POST -Uri "$BackendUrl/agents/cycle/start" -ErrorAction Stop
    Write-Host "✓ Scraping cycle completed" -ForegroundColor Green
    Write-Host "  Run ID: $($result.run_id)" -ForegroundColor Gray
    Write-Host "  Success: $($result.success)" -ForegroundColor Gray
    
    if ($result.metrics) {
        Write-Host "`n  Metrics:" -ForegroundColor Cyan
        Write-Host "    Sources scraped: $($result.metrics.sources_scraped)" -ForegroundColor Gray
        Write-Host "    Articles collected: $($result.metrics.articles_scraped)" -ForegroundColor Gray
        Write-Host "    Articles validated: $($result.metrics.articles_validated)" -ForegroundColor Gray
        Write-Host "    Articles stored: $($result.metrics.articles_stored)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "✗ Failed to trigger scraping cycle" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Wait and check new data
Write-Host "`n[4/5] Waiting for data processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $afterCount = python -c "from pymongo import MongoClient; c = MongoClient('$MongoUrl'); print(c.national_indicator.raw_articles.count_documents({}))"
    $indicatorCount = python -c "from pymongo import MongoClient; c = MongoClient('$MongoUrl'); print(c.national_indicator.indicator_calculations.count_documents({}))"
    
    Write-Host "✓ Data collection results:" -ForegroundColor Green
    Write-Host "  Articles in database: $afterCount (was: $beforeCount)" -ForegroundColor Gray
    Write-Host "  Indicator calculations: $indicatorCount" -ForegroundColor Gray
    
    if ([int]$afterCount -gt [int]$beforeCount) {
        Write-Host "`n  🎉 Success! New articles collected!" -ForegroundColor Green
    }
    elseif ([int]$afterCount -eq 0) {
        Write-Host "`n  ⚠ No articles yet. This might be the first run." -ForegroundColor Yellow
        Write-Host "  Some scrapers might have failed (common for first run)." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠ Could not verify data count" -ForegroundColor Yellow
}

# Step 5: Dashboard link
Write-Host "`n[5/5] Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open dashboard: http://localhost:3000/dashboard" -ForegroundColor Cyan
Write-Host "  2. Login with:" -ForegroundColor Cyan
Write-Host "     Email: admin@example.com" -ForegroundColor Gray
Write-Host "     Password: admin123" -ForegroundColor Gray
Write-Host "`n  3. To run another cycle, execute this script again" -ForegroundColor Cyan

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
