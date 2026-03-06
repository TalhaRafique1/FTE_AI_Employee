@echo off
REM ============================================================
REM LinkedIn Auto-Post - One Click Solution
REM ============================================================
REM This script:
REM 1. Starts MCP Server
REM 2. Opens LinkedIn
REM 3. Automatically posts your content
REM 4. No manual work needed!
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN AUTO-POST - One Click Solution
echo ============================================================
echo.

REM Step 1: Check if MCP is already running
echo [Step 1/5] Checking MCP Server...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if not errorlevel 1 (
    echo MCP Server is already running!
    goto :step2
)

echo MCP Server not running. Starting it now...
start "" cmd /c "npx @playwright/mcp@latest --port 8808 --shared-browser-context"
echo Waiting 10 seconds for MCP Server to start...
timeout /t 10 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 10 >nul

:step2
echo.
echo [Step 2/5] Finding LinkedIn post...
set "POST_FILE="

REM Find post file
if exist "AI_Employee_Vault\Approved\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Approved\*linkedin*.md) do (
        set "POST_FILE=%%f"
        goto :found
    )
)

if exist "AI_Employee_Vault\Done\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Done\*linkedin*.md) do (
        set "POST_FILE=%%f"
        goto :found
    )
)

if exist "AI_Employee_Vault\Social\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Social\*linkedin*.md) do (
        set "POST_FILE=%%f"
        goto :found
    )
)

:found
if "%POST_FILE%"=="" (
    echo ERROR: No LinkedIn post file found!
    echo.
    pause
    exit /b 1
)

echo Found: %POST_FILE%

echo.
echo [Step 3/5] Opening LinkedIn...
start https://www.linkedin.com/feed/
echo LinkedIn is opening in your browser...
timeout /t 5 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 5 >nul

echo.
echo [Step 4/5] Posting automatically...
echo Please wait while the AI Employee posts to LinkedIn...
echo.

REM Step 5: Run auto-poster
python linkedin_auto_post_v2.py "%POST_FILE%"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] Auto-posting failed!
    echo ============================================================
    echo.
    echo The post content is ready. Please post manually:
    echo 1. Go to: https://www.linkedin.com/feed/
    echo 2. Click "Start a post"
    echo 3. Copy and paste the content from the file
    echo.
    pause
    exit /b 1
)

echo.
echo [Step 5/5] SUCCESS!
echo.
echo ============================================================
echo YOUR POST IS LIVE ON LINKEDIN!
echo ============================================================
echo.
echo The AI Employee has automatically posted your content.
echo.
echo Post file: %POST_FILE%
echo.
echo You can view it at: https://www.linkedin.com/feed/
echo.
pause
