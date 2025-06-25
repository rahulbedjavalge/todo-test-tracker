# Universal Project Todo Tracker - Windows Setup Script
# Run this script in PowerShell to set up the project

Write-Host "🚀 Universal Project Todo Tracker - Windows Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check Python installation
Write-Host "`n📋 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Python found: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "  ❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check pip
Write-Host "`n📦 Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ pip found: $pipVersion" -ForegroundColor Green
    } else {
        throw "pip not found"
    }
} catch {
    Write-Host "  ❌ pip not found. Please ensure pip is installed" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📥 Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "  ❌ Failed to install dependencies. Check requirements.txt" -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host "`n🔧 Setting up environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file already exists" -ForegroundColor Green
} else {
    Write-Host "  📝 .env file not found. Copying from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "  ✅ .env file created from template" -ForegroundColor Green
    Write-Host "  ⚠️  Please edit .env file with your API keys" -ForegroundColor Yellow
}

# Run test
Write-Host "`n🧪 Running installation test..." -ForegroundColor Yellow
python test_installation.py

# Show completion message
Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "2. Run: python quick_start.py" -ForegroundColor White
Write-Host "3. Or run: python main.py --help" -ForegroundColor White

Write-Host "`n📚 Documentation: README.md" -ForegroundColor Cyan
Write-Host "🆘 Need help? Check the GitHub repository" -ForegroundColor Cyan
