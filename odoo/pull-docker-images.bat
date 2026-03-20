@echo off
REM Docker Pull Retry Script for Odoo
REM Helps with network connectivity issues when pulling large images

echo ======================================================================
echo Docker Pull Helper - Odoo Setup
echo ======================================================================
echo.
echo This script will attempt to pull Docker images with retries.
echo If pulls fail, you can still use Gold Tier without Odoo!
echo.
echo ======================================================================
echo.

cd /d "%~dp0"

REM Function to pull with retry
:pull_with_retry
set IMAGE_NAME=%1
set MAX_RETRIES=3
set RETRY=0

:retry_loop
if %RETRY% GEQ %MAX_RETRIES% (
    echo [ERROR] Failed to pull %IMAGE_NAME% after %MAX_RETRIES% attempts
    goto :eof
)

set /a RETRY=%RETRY%+1
echo [Attempt %RETRY%/%MAX_RETRIES%] Pulling %IMAGE_NAME%...
docker pull %IMAGE_NAME%

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pulled %IMAGE_NAME%
    goto :eof
) else (
    echo [FAILED] Retrying in 10 seconds...
    timeout /t 10 /nobreak >nul
    goto :retry_loop
)

echo.
echo ======================================================================
echo Step 1: Pull PostgreSQL (Alpine - smaller image)
echo ======================================================================
echo.

call :pull_with_retry postgres:15-alpine

echo.
echo ======================================================================
echo Step 2: Pull Odoo (large image - may take time)
echo ======================================================================
echo.

call :pull_with_retry odoo:17.0

echo.
echo ======================================================================
echo Step 3: Start Services
echo ======================================================================
echo.

set /p START_SERVICES="Start Odoo services now? (Y/N): "
if /i "%START_SERVICES%"=="Y" (
    echo Starting Docker Compose...
    docker-compose up -d
    
    echo.
    echo Waiting for services to start (30 seconds)...
    timeout /t 30 /nobreak
    
    echo.
    echo Checking service status...
    docker-compose ps
    
    echo.
    echo ======================================================================
    echo Odoo Setup Complete!
    echo ======================================================================
    echo.
    echo Access Odoo at: http://localhost:8069
    echo Odoo MCP Server will be available at: http://localhost:8810
    echo.
    echo Next steps:
    echo 1. Open http://localhost:8069 in your browser
    echo 2. Create your database
    echo 3. Install Accounting module
    echo 4. Test Odoo MCP connection
    echo.
) else (
    echo.
    echo Services not started. You can start them later with:
    echo   docker-compose up -d
    echo.
)

echo.
echo ======================================================================
echo Alternative: Use Gold Tier Without Odoo
echo ======================================================================
echo.
echo If you experienced Docker issues, you can still use Gold Tier:
echo.
echo   python orchestrator.py --continuous
echo.
echo Features that work without Odoo:
echo   - Facebook integration
echo   - LinkedIn integration
echo   - Ralph Wiggum Loop
echo   - CEO Briefing Generator
echo   - Gmail Watcher
echo   - Filesystem Watcher
echo.
echo Add Odoo later when network improves!
echo ======================================================================
echo.

pause
