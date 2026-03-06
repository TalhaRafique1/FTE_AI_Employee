@echo off
REM ============================================================
REM LinkedIn Auto-Post - FINAL WORKING VERSION
REM ============================================================
REM IMPORTANT: You must be logged in to LinkedIn first!
REM 
REM Usage:
REM 1. Login to LinkedIn in your browser first
REM 2. Run this script
REM 3. It will auto-post
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN AUTO-POST - FINAL VERSION
echo ============================================================
echo.
echo IMPORTANT: You MUST be logged in to LinkedIn first!
echo.
echo Step 1: Open LinkedIn and login (if not already)
echo.
pause

REM Open LinkedIn for login
start https://www.linkedin.com/login
echo.
echo Please login to LinkedIn in the browser window...
echo After you're logged in and see your feed, press Enter.
echo.
pause

echo.
echo Step 2: Starting MCP Server...
echo.

REM Check if MCP is running
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if not errorlevel 1 (
    echo MCP Server is already running.
) else (
    echo Starting MCP Server...
    start "" cmd /c "npx @playwright/mcp@latest --port 8808 --shared-browser-context"
    echo Waiting 15 seconds for MCP Server to start...
    timeout /t 15 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 15 >nul
)

echo.
echo Step 3: Finding post content...
echo.

REM Find post file
set "POST_FILE="
if exist "AI_Employee_Vault\Approved\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Approved\*linkedin*.md) do set "POST_FILE=%%f"
)
if exist "AI_Employee_Vault\Done\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Done\*linkedin*.md) do set "POST_FILE=%%f"
)

if "%POST_FILE%"=="" (
    echo ERROR: No LinkedIn post file found!
    pause
    exit /b 1
)

echo Found: %POST_FILE%

echo.
echo Step 4: Auto-posting to LinkedIn...
echo Please wait...
echo.

python linkedin_auto_post_v2.py "%POST_FILE%"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Auto-posting encountered an issue.
    echo ============================================================
    echo.
    echo But don't worry! LinkedIn should be open.
    echo Just copy the content from the file and paste manually.
    echo.
) else (
    echo.
    echo ============================================================
    echo SUCCESS! Your post is live on LinkedIn!
    echo ============================================================
)

echo.
pause
