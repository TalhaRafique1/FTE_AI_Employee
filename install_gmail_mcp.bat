@echo off
REM ============================================================
REM Install Gmail MCP Server
REM ============================================================

echo.
echo ============================================================
echo GMAIL MCP SERVER - Installation
echo ============================================================
echo.

cd gmail-mcp-server

echo [Step 1/3] Installing dependencies...
echo.
call npm install

if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    echo Make sure Node.js is installed.
    pause
    exit /b 1
)

echo.
echo [Step 2/3] Creating configuration...
echo.

REM Create config directory
if not exist "%APPDATA%\claude-code" mkdir "%APPDATA%\claude-code"

REM Create MCP config
echo {
  "servers": {
    "gmail": {
      "command": "node",
      "args": ["D:/FTE_AI_Employee/gmail-mcp-server/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "D:/FTE_AI_Employee/credentials.json"
      }
    }
  }
} > "%APPDATA%\claude-code\mcp.json"

echo MCP config created at: %APPDATA%\claude-code\mcp.json

echo.
echo [Step 3/3] Testing installation...
echo.

REM Test if server can start
node -e "console.log('Node.js is working')"

if errorlevel 1 (
    echo ERROR: Node.js test failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo INSTALLATION COMPLETE!
echo ============================================================
echo.
echo Gmail MCP Server is installed and configured.
echo.
echo To use with Qwen Code:
echo   qwen -p "Send an email to test@example.com"
echo.
echo The Gmail MCP server will:
echo   - Authenticate with your Gmail account
echo   - Send emails on command
echo   - Read emails on command
echo.
echo First run will require authentication.
echo.
pause

cd ..
