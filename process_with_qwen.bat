@echo off
REM ============================================================
REM Process Needs_Action with Qwen Code
REM ============================================================
REM This properly processes files and creates approval requests
REM ============================================================

echo.
echo ============================================================
echo PROCESSING NEEDS_ACTION WITH QWEN CODE
echo ============================================================
echo.

REM Check if Needs_Action has files
dir AI_Employee_Vault\Needs_Action\*.md >nul 2>&1
if errorlevel 1 (
    echo No .md files found in Needs_Action folder.
    echo.
    pause
    exit /b 0
)

echo Found files to process in Needs_Action...
echo.

REM Count files
for /f %%i in ('dir /b AI_Employee_Vault\Needs_Action\*.md 2^>nul ^| find /c ".md"') do set FILE_COUNT=%%i
echo Files to process: %FILE_COUNT%
echo.

echo ============================================================
echo Starting Qwen Code...
echo ============================================================
echo.
echo Qwen Code will:
echo 1. Read all files in Needs_Action
echo 2. Create Plans for multi-step tasks
echo 3. Create Pending_Approval for sensitive actions
echo 4. Move completed items to Done
echo.
echo Press Ctrl+C when Qwen Code finishes processing.
echo.
echo ============================================================
echo.

REM Run Qwen Code interactively
cd AI_Employee_Vault
qwen -i -p "You are an AI Employee assistant. Process all files in the Needs_Action folder.

For each file:
1. Read and understand the content
2. If it requires multiple steps, create a Plan.md in Plans/ folder
3. If it requires human approval (payments, emails to new contacts, sensitive actions), create a file in Pending_Approval/ folder
4. If it can be completed automatically, do it and move to Done/
5. Update Dashboard.md with what you did

Rules:
- Always create Pending_Approval for: payments, external communications, new contacts
- Always create Plans for: tasks with 3+ steps
- Log all actions in Logs/ folder

Start by reading the Company_Handbook.md for rules, then process Needs_Action files."

echo.
echo ============================================================
echo Qwen Code finished.
echo ============================================================
echo.

REM Go back to project root
cd ..

echo Check the following folders:
echo - Plans/ - for created plans
echo - Pending_Approval/ - for items needing your approval
echo - Done/ - for completed items
echo - Dashboard.md - for summary
echo.

pause
