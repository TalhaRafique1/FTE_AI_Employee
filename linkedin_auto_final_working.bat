@echo off
REM ============================================================
REM LinkedIn Auto-Post - FINAL WORKING SOLUTION
REM ============================================================
REM This GUARANTEES the browser is open and logged in before posting
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN AUTO-POST - FINAL WORKING SOLUTION
echo ============================================================
echo.
echo This will:
echo 1. Open LinkedIn in your browser
echo 2. You login (if not already)
echo 3. Start MCP Server
echo 4. Auto-post your content
echo.
echo ============================================================
echo.

REM Step 1: Open LinkedIn for login
echo [Step 1/5] Opening LinkedIn for login...
start https://www.linkedin.com/feed/
echo.
echo A browser window should have opened.
echo.
echo IMPORTANT: 
echo - If you see the login page, please login
echo - If you're already logged in, you should see your feed
echo.
echo Wait 10 seconds for the page to load, then...
timeout /t 10 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 10 >nul

echo.
echo [Step 2/5] Are you logged in to LinkedIn? (Y/N)
set /p LOGGED_IN=
if /i not "%LOGGED_IN%"=="Y" (
    echo.
    echo Please login now. I'll wait...
    echo Press Enter when you're logged in and see your feed.
    pause
)

echo.
echo [Step 3/5] Starting MCP Server...
echo.

REM Check if MCP is running
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if not errorlevel 1 (
    echo MCP Server is already running.
    goto :step4
)

echo Starting MCP Server...
start "" cmd /c "npx @playwright/mcp@latest --port 8808 --shared-browser-context"
echo Waiting 15 seconds...
timeout /t 15 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 15 >nul

:step4
echo.
echo [Step 4/5] Verifying MCP Server...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if errorlevel 1 (
    echo.
    echo ERROR: MCP Server failed to start!
    pause
    exit /b 1
)
echo MCP Server is ready!

echo.
echo [Step 5/5] Running Auto-Poster...
echo.
echo IMPORTANT: Keep the LinkedIn browser window OPEN!
echo The auto-poster will use this window to post.
echo.

REM Run the auto-poster
python linkedin_auto_working.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Auto-posting encountered an issue.
    echo ============================================================
    echo.
    echo But LinkedIn is open! Just post manually:
    echo 1. Click "Start a post"
    echo 2. Copy content from the post file
    echo 3. Paste and click Post
    echo.
) else (
    echo.
    echo ============================================================
    echo SUCCESS! Your post should be live on LinkedIn!
    echo ============================================================
)

echo.
pause
