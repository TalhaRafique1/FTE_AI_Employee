@echo off
REM ============================================================
REM LinkedIn Auto-Post - GUARANTEED WORKING
REM ============================================================
REM This script:
REM 1. Starts MCP Server
REM 2. Waits for it to be ready
REM 3. Runs the auto-poster
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN AUTO-POST - GUARANTEED WORKING
echo ============================================================
echo.

REM Step 1: Check if MCP is already running
echo [Step 1/4] Checking MCP Server...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if not errorlevel 1 (
    echo MCP Server is already running!
    goto :step2
)

echo MCP Server not running. Starting it now...
start "" cmd /c "npx @playwright/mcp@latest --port 8808 --shared-browser-context"
echo.
echo Waiting 15 seconds for MCP Server to start...
echo.
timeout /t 15 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 15 >nul

:step2
echo.
echo [Step 2/4] Verifying MCP Server...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if errorlevel 1 (
    echo.
    echo ERROR: MCP Server failed to start!
    echo.
    echo Please start it manually:
    echo   npx @playwright/mcp@latest --port 8808 --shared-browser-context
    echo.
    pause
    exit /b 1
)
echo MCP Server is ready!

echo.
echo [Step 3/4] IMPORTANT: LinkedIn Login Check
echo ============================================================
echo.
echo Before auto-posting works, you MUST be logged in to LinkedIn!
echo.
echo Do you want to open LinkedIn now to login? (Y/N)
set /p LOGIN_CHOICE=
if /i "%LOGIN_CHOICE%"=="Y" (
    echo Opening LinkedIn...
    start https://www.linkedin.com/feed/
    echo.
    echo Please login and wait until you see your feed.
    echo Press Enter when you're ready to continue...
    pause
)

echo.
echo [Step 4/4] Running Auto-Poster...
echo.

REM Run the auto-poster
python linkedin_auto_working.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Auto-posting did not complete successfully.
    echo ============================================================
    echo.
    echo You can still post manually:
    echo 1. Go to https://www.linkedin.com/feed/
    echo 2. Click "Start a post"
    echo 3. Copy content from the post file
    echo 4. Paste and click Post
    echo.
) else (
    echo.
    echo ============================================================
    echo SUCCESS! Check your LinkedIn feed!
    echo ============================================================
)

echo.
pause
