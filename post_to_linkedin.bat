@echo off
REM LinkedIn Post Helper - Opens LinkedIn and shows post content

echo ============================================================
echo LinkedIn Post Helper
echo ============================================================
echo.
echo This script will:
echo 1. Open LinkedIn in your browser
echo 2. Show you the post content to copy
echo.
echo ============================================================
echo.

REM Open LinkedIn
start https://www.linkedin.com/feed/

echo LinkedIn is opening in your browser...
echo.
echo Please wait 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo POST CONTENT (Copy this and paste on LinkedIn):
echo ============================================================
echo.

REM Read and display the latest LinkedIn post draft
if exist "AI_Employee_Vault\Social\*.md" (
    echo Latest post from Social folder:
    type "AI_Employee_Vault\Social\*.md"
) else if exist "AI_Employee_Vault\Done\*.md" (
    echo Latest post from Done folder:
    type "AI_Employee_Vault\Done\*.md"
) else (
    echo No post drafts found!
    echo.
    echo Please create a post draft in AI_Employee_Vault\Social\ folder
)

echo.
echo ============================================================
echo.
echo NEXT STEPS:
echo 1. Click "Start a post" on LinkedIn
echo 2. Copy the content above (Ctrl+C)
echo 3. Paste on LinkedIn (Ctrl+V)
echo 4. Click "Post"
echo ============================================================
echo.
pause
