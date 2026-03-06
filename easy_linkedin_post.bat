@echo off
REM ============================================================
REM LinkedIn Post Helper - Easy Method
REM ============================================================
REM This script:
REM 1. Opens LinkedIn in your browser
REM 2. Shows you the post content
REM 3. You copy and paste manually
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN POST HELPER - Easy Method
echo ============================================================
echo.

REM Step 1: Open LinkedIn
echo [Step 1/4] Opening LinkedIn in your browser...
start https://www.linkedin.com/feed/
echo Done! LinkedIn should be open now.
echo.

REM Wait for browser to open
echo Waiting 5 seconds for LinkedIn to load...
timeout /t 5 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 5 >nul

REM Step 2: Find and show post content
echo [Step 2/4] Finding post content...
echo.

set "POST_FILE="

REM Check Approved folder first
if exist "AI_Employee_Vault\Approved\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Approved\*linkedin*.md) do (
        set "POST_FILE=%%f"
        goto :found
    )
)

REM Check Done folder
if exist "AI_Employee_Vault\Done\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Done\*linkedin*.md) do (
        set "POST_FILE=%%f"
        goto :found
    )
)

REM Check Social folder
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
    echo Please create a post draft in AI_Employee_Vault\Social\ folder
    echo.
    pause
    exit /b 1
)

echo Found post file: %POST_FILE%
echo.

REM Step 3: Display post content
echo [Step 3/4] POST CONTENT (Copy this):
echo ============================================================
echo.

REM Extract and display content (skip frontmatter)
set "skip_frontmatter=0"
set "in_post_content=0"

for /f "usebackq tokens=*" %%a in ("%POST_FILE%") do (
    set "line=%%a"
    
    REM Skip frontmatter (lines between ---)
    if "!line!"=="---" (
        if !skip_frontmatter!==0 (
            set "skip_frontmatter=1"
        ) else (
            set "skip_frontmatter=0"
        )
        goto :next
    )
    
    if !skip_frontmatter!==1 goto :next
    
    REM Show Post Content section
    echo !line!
    
    :next
)

echo.
echo ============================================================
echo.

REM Step 4: Instructions
echo [Step 4/4] NEXT STEPS:
echo ============================================================
echo.
echo 1. LinkedIn should be open in your browser
echo    If not, go to: https://www.linkedin.com/feed/
echo.
echo 2. Click "Start a post" button at the top of your feed
echo.
echo 3. Copy the content above (select all, then Ctrl+C)
echo.
echo 4. Paste into LinkedIn post box (Ctrl+V)
echo.
echo 5. Click "Post" button
echo.
echo ============================================================
echo.
echo Need help? Check the post file:
echo %POST_FILE%
echo.
pause
