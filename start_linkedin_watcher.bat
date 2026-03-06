@echo off
REM Start LinkedIn Watcher with MCP Server
REM This script starts both the MCP server and the LinkedIn watcher

echo ============================================================
echo LinkedIn Watcher - Silver Tier
echo ============================================================
echo.

REM Check if Node.js is installed
where npx >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js/npx not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Starting Playwright MCP Server...
echo.

REM Start MCP server in background
start "Playwright MCP Server" cmd /k "npx @playwright/mcp@latest --port 8808 --shared-browser-context"

echo Waiting for MCP server to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting LinkedIn Watcher...
echo.

REM Start LinkedIn watcher
python watchers\linkedin_watcher.py

echo.
echo LinkedIn Watcher stopped.
echo You can close the MCP Server window manually.
pause
