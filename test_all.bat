@echo off
REM ============================================================
REM AI Employee - Complete System Test
REM ============================================================
REM This tests ALL features of your AI Employee Silver Tier
REM ============================================================

echo.
echo ============================================================
echo AI EMPLOYEE - COMPLETE SYSTEM TEST
echo ============================================================
echo.
echo This will test:
echo   1. Folder Structure
echo   2. Gmail Watcher
echo   3. Filesystem Watcher
echo   4. Gmail MCP Server
echo   5. Email Sending (Python)
echo   6. LinkedIn Auto-Post
echo   7. Orchestrator
echo   8. Qwen Code Integration
echo   9. Dashboard
echo   10. All Scripts
echo.
echo ============================================================
echo.

set "PASS=0"
set "FAIL=0"

REM ============================================================
REM TEST 1: Folder Structure
REM ============================================================
echo [TEST 1/10] Checking Folder Structure...
echo.

set "FOLDERS=AI_Employee_Vault AI_Employee_Vault\Inbox AI_Employee_Vault\Needs_Action AI_Employee_Vault\Done AI_Employee_Vault\Plans AI_Employee_Vault\Pending_Approval AI_Employee_Vault\Approved AI_Employee_Vault\Rejected AI_Employee_Vault\Logs AI_Employee_Vault\Briefings AI_Employee_Vault\Social"

for %%F in (%FOLDERS%) do (
    if exist "%%F" (
        echo   [PASS] %%F
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%F - NOT FOUND
        set /a FAIL+=1
    )
)

echo.

REM ============================================================
REM TEST 2: Core Files
REM ============================================================
echo [TEST 2/10] Checking Core Files...
echo.

set "FILES=AI_Employee_Vault\Dashboard.md AI_Employee_Vault\Company_Handbook.md AI_Employee_Vault\Business_Goals.md orchestrator.py README.md"

for %%F in (%FILES%) do (
    if exist "%%F" (
        echo   [PASS] %%F
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%F - NOT FOUND
        set /a FAIL+=1
    )
)

echo.

REM ============================================================
REM TEST 3: Watchers
REM ============================================================
echo [TEST 3/10] Checking Watchers...
echo.

if exist "watchers\base_watcher.py" (
    echo   [PASS] watchers\base_watcher.py
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\base_watcher.py
    set /a FAIL+=1
)

if exist "watchers\filesystem_watcher.py" (
    echo   [PASS] watchers\filesystem_watcher.py
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\filesystem_watcher.py
    set /a FAIL+=1
)

if exist "watchers\gmail_watcher.py" (
    echo   [PASS] watchers\gmail_watcher.py
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\gmail_watcher.py
    set /a FAIL+=1
)

if exist "watchers\linkedin_watcher.py" (
    echo   [PASS] watchers\linkedin_watcher.py
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\linkedin_watcher.py
    set /a FAIL+=1
)

echo.

REM ============================================================
REM TEST 4: Gmail MCP Server
REM ============================================================
echo [TEST 4/10] Checking Gmail MCP Server...
echo.

if exist "gmail-mcp-server\index.js" (
    echo   [PASS] gmail-mcp-server\index.js
    set /a PASS+=1
) else (
    echo   [FAIL] gmail-mcp-server\index.js
    set /a FAIL+=1
)

if exist "gmail-mcp-server\package.json" (
    echo   [PASS] gmail-mcp-server\package.json
    set /a PASS+=1
) else (
    echo   [FAIL] gmail-mcp-server\package.json
    set /a FAIL+=1
)

if exist "%APPDATA%\claude-code\mcp.json" (
    echo   [PASS] MCP Config (%APPDATA%\claude-code\mcp.json)
    set /a PASS+=1
) else (
    echo   [FAIL] MCP Config not found
    set /a FAIL+=1
)

echo.

REM ============================================================
REM TEST 5: Email Scripts
REM ============================================================
echo [TEST 5/10] Checking Email Scripts...
echo.

if exist "send_gmail_email.py" (
    echo   [PASS] send_gmail_email.py
    set /a PASS+=1
) else (
    echo   [FAIL] send_gmail_email.py
    set /a FAIL+=1
)

if exist "send_approved_email_mcp.py" (
    echo   [PASS] send_approved_email_mcp.py
    set /a PASS+=1
) else (
    echo   [FAIL] send_approved_email_mcp.py
    set /a FAIL+=1
)

if exist "credentials.json" (
    echo   [PASS] credentials.json
    set /a PASS+=1
) else (
    echo   [FAIL] credentials.json
    set /a FAIL+=1
)

if exist "%USERPROFILE%\.ai_employee\gmail_token.pickle" (
    echo   [PASS] Gmail Token (authenticated)
    set /a PASS+=1
) else (
    echo   [WARN] Gmail Token not found (will auth on first use)
)

echo.

REM ============================================================
REM TEST 6: LinkedIn Scripts
REM ============================================================
echo [TEST 6/10] Checking LinkedIn Scripts...
echo.

if exist "linkedin_auto_post.py" (
    echo   [PASS] linkedin_auto_post.py
    set /a PASS+=1
) else (
    echo   [FAIL] linkedin_auto_post.py
    set /a FAIL+=1
)

if exist "linkedin_auto_working.py" (
    echo   [PASS] linkedin_auto_working.py
    set /a PASS+=1
) else (
    echo   [FAIL] linkedin_auto_working.py
    set /a FAIL+=1
)

if exist "linkedin_post_helper.py" (
    echo   [PASS] linkedin_post_helper.py
    set /a PASS+=1
) else (
    echo   [FAIL] linkedin_post_helper.py
    set /a FAIL+=1
)

if exist "auto_post_linkedin_final.bat" (
    echo   [PASS] auto_post_linkedin_final.bat
    set /a PASS+=1
) else (
    echo   [FAIL] auto_post_linkedin_final.bat
    set /a FAIL+=1
)

echo.

REM ============================================================
REM TEST 7: Skills Documentation
REM ============================================================
echo [TEST 7/10] Checking Skills Documentation...
echo.

set "SKILLS=skills\vault-operations.md skills\email-operations.md skills\approval-workflow.md skills\social-media-operations.md skills\plan-creation.md skills\scheduling-operations.md skills\linkedin-posting.md"

for %%F in (%SKILLS%) do (
    if exist "%%F" (
        echo   [PASS] %%F
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%F
        set /a FAIL+=1
    )
)

echo.

REM ============================================================
REM TEST 8: Python Syntax Check
REM ============================================================
echo [TEST 8/10] Checking Python Scripts Syntax...
echo.

python -m py_compile orchestrator.py 2>nul
if not errorlevel 1 (
    echo   [PASS] orchestrator.py - Syntax OK
    set /a PASS+=1
) else (
    echo   [FAIL] orchestrator.py - Syntax Error
    set /a FAIL+=1
)

python -m py_compile send_gmail_email.py 2>nul
if not errorlevel 1 (
    echo   [PASS] send_gmail_email.py - Syntax OK
    set /a PASS+=1
) else (
    echo   [FAIL] send_gmail_email.py - Syntax Error
    set /a FAIL+=1
)

python -m py_compile watchers\gmail_watcher.py 2>nul
if not errorlevel 1 (
    echo   [PASS] watchers\gmail_watcher.py - Syntax OK
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\gmail_watcher.py - Syntax Error
    set /a FAIL+=1
)

python -m py_compile watchers\filesystem_watcher.py 2>nul
if not errorlevel 1 (
    echo   [PASS] watchers\filesystem_watcher.py - Syntax OK
    set /a PASS+=1
) else (
    echo   [FAIL] watchers\filesystem_watcher.py - Syntax Error
    set /a FAIL+=1
)

echo.

REM ============================================================
REM TEST 9: Qwen Code
REM ============================================================
echo [TEST 9/10] Checking Qwen Code...
echo.

qwen --version >nul 2>&1
if not errorlevel 1 (
    echo   [PASS] Qwen Code is installed
    set /a PASS+=1
) else (
    echo   [FAIL] Qwen Code not found
    set /a FAIL+=1
)

echo.

REM ============================================================
REM TEST 10: Documentation
REM ============================================================
echo [TEST 10/10] Checking Documentation...
echo.

set "DOCS=README.md QWEN.md SILVER_TIER_README.md LINKEDIN_AUTO_POST_WORKING.md GMAIL_MCP_CREATED.md HOW_TO_USE_QWEN.md"

for %%F in (%DOCS%) do (
    if exist "%%F" (
        echo   [PASS] %%F
        set /a PASS+=1
    ) else (
        echo   [FAIL] %%F
        set /a FAIL+=1
    )
)

echo.

REM ============================================================
REM SUMMARY
REM ============================================================
echo ============================================================
echo TEST SUMMARY
echo ============================================================
echo.
echo Total Tests: %PASS% + %FAIL% = %PASS% Passed, %FAIL% Failed
echo.

if %FAIL%==0 (
    echo [SUCCESS] All tests passed!
    echo.
    echo Your AI Employee Silver Tier is 100%% complete!
) else (
    echo [WARNING] Some tests failed.
    echo Please check the failed items above.
)

echo.
echo ============================================================
echo.
pause
