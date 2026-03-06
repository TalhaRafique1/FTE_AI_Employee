@echo off
REM Quick LinkedIn Post Test

echo ============================================================
echo LinkedIn Post - Quick Test
echo ============================================================
echo.

REM Check if MCP server is running
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py list -u http://localhost:8808 2>&1 | findstr "browser_navigate" >nul
if errorlevel 1 (
    echo ERROR: MCP server is not running!
    echo.
    echo Please start it first:
    echo   npx @playwright/mcp@latest --port 8808 --shared-browser-context
    echo.
    pause
    exit /b 1
)

echo MCP Server is running!
echo.

REM Open LinkedIn
echo Opening LinkedIn...
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call -u http://localhost:8808 -t browser_navigate -p "{\"url\": \"https://www.linkedin.com/feed/\"}"

echo.
echo ============================================================
echo LinkedIn should be open in your browser now!
echo.
echo NEXT STEPS:
echo 1. Click "Start a post" on LinkedIn
echo 2. Copy this content:
echo.
echo --- COPY BELOW ---
echo.
echo Achievement Unlocked!
echo.
echo I've completed building my Personal AI Employee - Silver Tier!
echo.
echo Features:
echo - Gmail integration
echo - LinkedIn monitoring
echo - Task automation with Qwen Code
echo.
echo #AIEmployee #Automation #AI
echo.
echo --- COPY ABOVE ---
echo.
echo 3. Paste and click Post
echo ============================================================
echo.
pause
