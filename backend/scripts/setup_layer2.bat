@echo off
REM Layer 2 Setup Script for Windows
REM This script sets up the complete Layer 2 environment

echo ==================================
echo Layer 2 Setup Script (Windows)
echo ==================================
echo.

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the backend directory
    echo    cd backend
    echo    scripts\setup_layer2.bat
    exit /b 1
)

echo Step 1: Starting Docker containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Error: Failed to start Docker containers
    echo Make sure Docker Desktop is running
    exit /b 1
)

echo Waiting for databases to be ready (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo Step 2: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    exit /b 1
)

echo.
echo Step 3: Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo Step 4: Testing database connections...
python scripts\init_databases.py

echo.
echo Step 5: Running Alembic migrations...
alembic upgrade head
if %errorlevel% neq 0 (
    echo Error: Migration failed
    exit /b 1
)

echo.
echo Step 6: Verifying setup...
python scripts\init_databases.py

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Start the FastAPI server:
echo    uvicorn app.main:app --reload
echo.
echo 2. Access the API docs:
echo    http://localhost:8000/api/docs
echo.
echo 3. Access database management UIs:
echo    - pgAdmin:         http://localhost:5050
echo    - Mongo Express:   http://localhost:8081
echo    - Redis Commander: http://localhost:8082
echo.

pause
