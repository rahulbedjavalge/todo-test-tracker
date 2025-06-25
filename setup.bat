@echo off
REM Universal Project Todo Tracker - Quick Setup for Windows
echo 🚀 Universal Project Todo Tracker - Quick Setup
echo ============================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Copy .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy ".env.example" ".env"
    echo ⚠️  Please edit .env file with your API keys
)

REM Run quick start
echo 🚀 Starting quick setup...
python quick_start.py

pause
