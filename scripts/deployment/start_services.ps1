# CBAC System - Start All Services

Write-Host "🚀 Starting CBAC System..." -ForegroundColor Cyan
Write-Host ""

# Start Docker containers
Write-Host "📦 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

# Wait for containers to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check Qdrant
Write-Host ""
Write-Host "🔍 Checking Qdrant..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Qdrant is running on http://localhost:6333" -ForegroundColor Green
} catch {
    Write-Host "❌ Qdrant is not responding" -ForegroundColor Red
}

# Check MongoDB
Write-Host ""
Write-Host "🔍 Checking MongoDB..." -ForegroundColor Yellow
$mongoCheck = docker exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "db.version()" --quiet 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MongoDB is running on localhost:27017" -ForegroundColor Green
} else {
    Write-Host "❌ MongoDB is not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "✨ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Load data: python vector_db_save.py ; python mongo_db_save.py"
Write-Host "2. Run preflight: cd cbac_api ; python preflight_check.py"
Write-Host "3. Start API: python main.py"
