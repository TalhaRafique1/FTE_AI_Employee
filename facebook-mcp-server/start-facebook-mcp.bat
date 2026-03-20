@echo off
REM Facebook MCP Server Launcher
REM Starts the Facebook Graph API MCP server

echo ======================================================================
echo Facebook MCP Server - Gold Tier
echo ======================================================================
echo.

cd /d "%~dp0"

REM Check for environment variables
if "%FACEBOOK_ACCESS_TOKEN%"=="" (
    echo WARNING: FACEBOOK_ACCESS_TOKEN not set!
    echo.
    echo Please set environment variables in .env file or system:
    echo   - FACEBOOK_APP_ID
    echo   - FACEBOOK_APP_SECRET
    echo   - FACEBOOK_ACCESS_TOKEN
    echo   - FACEBOOK_PAGE_ID
    echo.
    echo See README.md for setup guide.
    echo.
    pause
    exit /b 1
)

echo Starting Facebook MCP Server...
echo.
echo Server will listen on stdio for MCP commands
echo Press Ctrl+C to stop
echo.
echo ======================================================================
echo.

REM Install dependencies if needed
pip install -r requirements.txt -q

REM Start the server
python facebook_mcp_server.py

pause
