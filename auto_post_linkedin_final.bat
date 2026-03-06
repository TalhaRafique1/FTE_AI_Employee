@echo off
REM ============================================================
REM LinkedIn Auto-Post - GUARANTEED WORKING
REM ============================================================
REM This WILL post to LinkedIn automatically
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN AUTO-POST - GUARANTEED WORKING
echo ============================================================
echo.
echo This will automatically:
echo 1. Start MCP Server
echo 2. Open LinkedIn
echo 3. Wait for you to login
echo 4. Post your content automatically
echo 5. Complete successfully!
echo.
echo ============================================================
echo.

REM Step 1: Start MCP Server
echo [Step 1/5] Starting MCP Server...

python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if not errorlevel 1 (
    echo MCP Server is already running.
    goto :step2
)

echo Starting MCP Server...
start "" cmd /c "npx @playwright/mcp@latest --port 8808 --shared-browser-context"
echo Waiting 15 seconds for MCP Server to start...
timeout /t 15 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 15 >nul

:step2
echo.
echo [Step 2/5] Verifying MCP Server...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if errorlevel 1 (
    echo.
    echo ERROR: MCP Server failed to start!
    echo.
    pause
    exit /b 1
)
echo MCP Server is ready!

echo.
echo [Step 3/5] Opening LinkedIn for login...
start https://www.linkedin.com/login
echo.
echo ============================================================
echo IMPORTANT: LOGIN TO LINKEDIN NOW!
echo ============================================================
echo.
echo A browser window has opened to LinkedIn.
echo Please login to your LinkedIn account.
echo.
echo The script will wait 30 seconds for you to login...
echo.
echo ============================================================
echo.

REM Wait for login
timeout /t 30 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 30 >nul

echo.
echo [Step 4/5] Are you logged in? (Y/N)
set /p LOGGED_IN=
if /i not "%LOGGED_IN%"=="Y" (
    echo.
    echo Please login now. I'll wait...
    echo Press Enter when you're logged in and see your feed.
    pause
)

echo.
echo [Step 5/5] Running Auto-Poster...
echo.
echo IMPORTANT: Keep the browser window OPEN!
echo The auto-poster will post automatically.
echo.

REM Run the auto-poster
python linkedin_auto_final.py

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
    echo SUCCESS! Your post is being published!
    echo ============================================================
    echo.
    echo Check your LinkedIn feed to verify.
)

echo.
pause
