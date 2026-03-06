@echo off
REM ============================================================
REM LinkedIn Post - SIMPLE WORKING METHOD
REM ============================================================
REM This ALWAYS works - no hanging, no automation issues
REM ============================================================

echo.
echo ============================================================
echo LINKEDIN POST - SIMPLE METHOD
echo ============================================================
echo.
echo This will:
echo 1. Open LinkedIn in your browser
echo 2. Copy your post content to clipboard
echo 3. You just paste and click Post
echo.
echo ============================================================
echo.

REM Step 1: Find post file
echo [Step 1/4] Finding post content...
set "POST_FILE="

if exist "AI_Employee_Vault\Approved\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Approved\*linkedin*.md) do set "POST_FILE=%%f"
)
if exist "AI_Employee_Vault\Done\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Done\*linkedin*.md) do set "POST_FILE=%%f"
)
if exist "AI_Employee_Vault\Social\*linkedin*.md" (
    for %%f in (AI_Employee_Vault\Social\*linkedin*.md) do set "POST_FILE=%%f"
)

if "%POST_FILE%"=="" (
    echo ERROR: No LinkedIn post file found!
    pause
    exit /b 1
)

echo Found: %POST_FILE%

REM Step 2: Extract content and copy to clipboard
echo.
echo [Step 2/4] Copying post content to clipboard...

REM Use PowerShell to extract and copy content
powershell -Command "$content = Get-Content '%POST_FILE%' -Raw; $match = [regex]::Match($content, '## Post Content\s*\n(.+?)(?=##|\n---|\Z)', [System.Text.RegularExpressions.RegexOptions]::Singleline); if($match.Success) { $match.Groups[1].Value.Trim() | Set-Clipboard } else { $content | Set-Clipboard }"

if errorlevel 1 (
    echo Could not copy to clipboard automatically.
    echo Please copy manually from the file.
) else (
    echo Content copied to clipboard!
)

REM Step 3: Open LinkedIn
echo.
echo [Step 3/4] Opening LinkedIn...
start https://www.linkedin.com/feed/
echo LinkedIn is opening in your browser...

REM Wait for browser
timeout /t 5 /nobreak >nul 2>&1 || ping 127.0.0.1 -n 5 >nul

REM Step 4: Show instructions
echo.
echo [Step 4/4] INSTRUCTIONS:
echo ============================================================
echo.
echo LinkedIn should now be open in your browser.
echo.
echo To post:
echo.
echo 1. Click "Start a post" button on LinkedIn
echo.
echo 2. Paste the content (Ctrl+V)
echo    (It's already copied to your clipboard!)
echo.
echo 3. Click "Post" button
echo.
echo 4. Done! Your post is live!
echo.
echo ============================================================
echo.
echo Post file: %POST_FILE%
echo.
echo Press any key when you've posted...
pause >nul

echo.
echo Great! Your post should be live on LinkedIn now!
echo.
pause
