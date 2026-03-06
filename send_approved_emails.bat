@echo off
REM ============================================================
REM Gmail MCP - Send Approved Emails
REM ============================================================
REM This sends all approved emails automatically via Gmail MCP
REM ============================================================

echo.
echo ============================================================
echo GMAIL MCP - AUTO-SEND APPROVED EMAILS
echo ============================================================
echo.
echo This will:
echo 1. Find all approved emails in Approved/ folder
echo 2. Send them via Gmail API
echo 3. Move sent emails to Done/ folder
echo.
echo ============================================================
echo.

cd gmail-mcp-server

echo [Step 1/2] Checking for approved emails...
echo.

dir ..\AI_Employee_Vault\Approved\EMAIL_*.md >nul 2>&1
if errorlevel 1 (
    echo No approved emails found in Approved folder.
    echo.
    echo To approve an email:
    echo   move AI_Employee_Vault\Pending_Approval\*.md AI_Employee_Vault\Approved\
    echo.
    pause
    exit /b 0
)

echo Approved emails found!
echo.

echo [Step 2/2] Sending emails via Gmail MCP...
echo.

node mcp-send-approved-emails.js

if errorlevel 1 (
    echo.
    echo ============================================================
    echo Email sending encountered errors.
    echo ============================================================
    echo.
    echo Check the error messages above.
    echo You can also use the Python sender as backup:
    echo   python ..\send_gmail_email.py --process-approved
    echo.
) else (
    echo.
    echo ============================================================
    echo SUCCESS! All approved emails sent!
    echo ============================================================
    echo.
    echo Check your Gmail Sent folder to verify.
    echo.
)

cd ..
pause
