# ============================================
# National Activity Indicator - Continuous Data Collection
# ============================================
# Runs scraping cycles periodically for testing

param(
    [int]$IntervalMinutes = 30,  # How often to run (default: 30 minutes)
    [int]$MaxCycles = 0           # 0 = run forever, or specify number of cycles
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Continuous Data Collection Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Interval: $IntervalMinutes minutes" -ForegroundColor Gray
Write-Host "Max cycles: $(if ($MaxCycles -eq 0) { 'Unlimited' } else { $MaxCycles })" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

$BackendUrl = "http://localhost:8080/api/v1"
$cycleCount = 0

while ($true) {
    $cycleCount++
    
    if ($MaxCycles -gt 0 -and $cycleCount -gt $MaxCycles) {
        Write-Host "`n✓ Completed $MaxCycles cycles. Exiting." -ForegroundColor Green
        break
    }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Starting cycle #$cycleCount" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    try {
        # Trigger scraping
        Write-Host "Triggering data collection..." -ForegroundColor Yellow
        $result = Invoke-RestMethod -Method POST -Uri "$BackendUrl/agents/cycle/start" -TimeoutSec 180
        
        if ($result.success) {
            Write-Host "✓ Cycle completed successfully" -ForegroundColor Green
            
            if ($result.metrics) {
                Write-Host "  Articles scraped: $($result.metrics.articles_scraped)" -ForegroundColor Gray
                Write-Host "  Articles validated: $($result.metrics.articles_validated)" -ForegroundColor Gray
                Write-Host "  Articles stored: $($result.metrics.articles_stored)" -ForegroundColor Gray
            }
        }
        else {
            Write-Host "⚠ Cycle completed with errors" -ForegroundColor Yellow
            if ($result.errors) {
                Write-Host "  Errors: $($result.errors.Count)" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "✗ Cycle failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check data counts
    try {
        $articleCount = python -c "from pymongo import MongoClient; c = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'); print(c.national_indicator.raw_articles.count_documents({}))"
        $indicatorCount = python -c "from pymongo import MongoClient; c = MongoClient('mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'); print(c.national_indicator.indicator_calculations.count_documents({}))"
        
        Write-Host "`nCurrent database state:" -ForegroundColor Cyan
        Write-Host "  Total articles: $articleCount" -ForegroundColor Gray
        Write-Host "  Total indicator calcs: $indicatorCount" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠ Could not query database" -ForegroundColor Yellow
    }
    
    if ($MaxCycles -eq 0 -or $cycleCount -lt $MaxCycles) {
        Write-Host "`nWaiting $IntervalMinutes minutes until next cycle..." -ForegroundColor Yellow
        Write-Host "Dashboard: http://localhost:3000/dashboard" -ForegroundColor Cyan
        Write-Host "========================================`n" -ForegroundColor Gray
        Start-Sleep -Seconds ($IntervalMinutes * 60)
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Data collection stopped" -ForegroundColor Cyan
Write-Host "Total cycles completed: $cycleCount" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
