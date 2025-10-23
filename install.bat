@echo off
REM FileFlow Windows Installer
REM Automatically installs all dependencies and sets up FileFlow

setlocal enabledelayedexpansion

REM Colors for output (using echo with special characters)
set "GREEN=[92m"
set "BLUE=[94m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

echo.
echo %BLUE%================================%NC%
echo %BLUE%  FileFlow Installation Script  %NC%
echo %BLUE%================================%NC%
echo.
echo This script will install FileFlow and all its dependencies.
echo.
set /p "confirm=Continue with installation? (Y/n): "
if /i "%confirm%"=="n" (
    echo Installation cancelled.
    exit /b 0
)

echo.
echo %BLUE%[STEP]%NC% Checking Python installation...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[SUCCESS]%NC% Python %PYTHON_VERSION% detected

echo.
echo %BLUE%[STEP]%NC% Checking Node.js installation (for web UI)...

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Node.js is not installed. Web UI will not be available.
    echo To install Node.js, visit: https://nodejs.org/
    echo Desktop UI and CLI will still work.
    set HAS_NODEJS=false
) else (
    for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
    echo %GREEN%[SUCCESS]%NC% Node.js !NODE_VERSION! detected
    set HAS_NODEJS=true
)

echo.
echo %BLUE%[STEP]%NC% Upgrading pip...
python -m pip install --upgrade pip --user

echo.
echo %BLUE%[STEP]%NC% Installing Python dependencies...
if exist requirements.txt (
    python -m pip install --user -r requirements.txt
    echo %GREEN%[SUCCESS]%NC% Python dependencies installed
) else (
    echo %RED%[ERROR]%NC% requirements.txt not found
    pause
    exit /b 1
)

REM Install Node.js dependencies if available
if "%HAS_NODEJS%"=="true" (
    echo.
    echo %BLUE%[STEP]%NC% Installing Node.js dependencies for web UI...
    if exist web\package.json (
        cd web
        echo Installing npm packages...
        call npm install
        if errorlevel 1 (
            echo %YELLOW%[WARNING]%NC% Some npm packages failed to install
        ) else (
            echo %GREEN%[SUCCESS]%NC% Node.js dependencies installed
        )
        cd ..
    )
)

echo.
echo %BLUE%[STEP]%NC% Creating configuration directory...
set "CONFIG_DIR=%USERPROFILE%\.config\fileflow"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

REM Create default config if it doesn't exist
if not exist "%CONFIG_DIR%\config.yaml" (
    echo Creating default configuration...
    (
        echo # FileFlow Configuration
        echo # Edit this file to customize your file organization
        echo.
        echo source_directories:
        echo   - "%USERPROFILE%\Downloads"
        echo.
        echo destination_directories:
        echo   Images: "%USERPROFILE%\Pictures\Organized"
        echo   Videos: "%USERPROFILE%\Videos\Organized"
        echo   Documents: "%USERPROFILE%\Documents\Organized"
        echo.
        echo # Enhanced content classification settings
        echo content_classification:
        echo   enabled: true
        echo   visual_analysis: true
        echo   filename_analysis: true
        echo   media_only: true
        echo   visual_threshold: 0.5
        echo   nsfw_notifications: false
        echo.
        echo # File type mappings
        echo file_types:
        echo   Images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]
        echo   Videos: [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".m4v"]
        echo   Documents: [".pdf", ".doc", ".docx", ".txt", ".rtf"]
    ) > "%CONFIG_DIR%\config.yaml"
    echo %GREEN%[SUCCESS]%NC% Default configuration created
)

echo.
echo %BLUE%[STEP]%NC% Creating launcher scripts...

REM Create desktop launcher
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo python -m fileflow.main --ui
    echo pause
) > launch-desktop.bat
echo %GREEN%[SUCCESS]%NC% Desktop launcher created: launch-desktop.bat

REM Create web launcher if Node.js is available
if "%HAS_NODEJS%"=="true" (
    (
        echo @echo off
        echo cd /d "%%~dp0"
        echo echo.
        echo echo Starting FileFlow Web UI...
        echo echo ================================
        echo echo.
        echo echo Services:
        echo echo   - API Server: http://localhost:9001
        echo echo   - Web UI: http://localhost:5173
        echo echo   - API Docs: http://localhost:9001/docs
        echo echo.
        echo echo Press Ctrl+C to stop
        echo echo.
        echo.
        echo REM Start API server
        echo start /b python -m fileflow.main --web --host 127.0.0.1 --port 9001
        echo.
        echo REM Wait for API to start
        echo timeout /t 2 /nobreak ^>nul
        echo.
        echo REM Start frontend
        echo cd web
        echo call npm run dev
    ) > launch-web.bat
    echo %GREEN%[SUCCESS]%NC% Web launcher created: launch-web.bat
)

REM Create CLI helper
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo python -m fileflow.main %%*
) > fileflow.bat
echo %GREEN%[SUCCESS]%NC% CLI helper created: fileflow.bat

echo.
echo %GREEN%================================%NC%
echo %GREEN%   Installation Complete!      %NC%
echo %GREEN%================================%NC%
echo.
echo %BLUE%FileFlow has been successfully installed with:%NC%
echo - Advanced content classification capabilities
echo - Multi-layered NSFW/SFW detection
echo - EXIF metadata analysis
echo - Visual content analysis
if "%HAS_NODEJS%"=="true" (
    echo - Modern web interface
)
echo.
echo %BLUE%Quick Start:%NC%
if "%HAS_NODEJS%"=="true" (
    echo - Launch Web UI: %YELLOW%launch-web.bat%NC%
    echo   Access at: %YELLOW%http://localhost:5173%NC%
    echo.
)
echo - Launch Desktop UI: %YELLOW%launch-desktop.bat%NC%
echo - CLI Usage: %YELLOW%fileflow.bat --help%NC%
echo.
echo %BLUE%Command Examples:%NC%
echo - Organize once: %YELLOW%fileflow.bat --organize-once%NC%
echo - Start watcher: %YELLOW%fileflow.bat --watch%NC%
echo - Reorganize with NSFW classification: %YELLOW%fileflow.bat --reorganize%NC%
echo.
echo %BLUE%Configuration:%NC%
echo - Config file: %YELLOW%%CONFIG_DIR%\config.yaml%NC%
echo - Or use the web/desktop UI to configure
echo.
echo %BLUE%Documentation:%NC%
if "%HAS_NODEJS%"=="true" (
    echo - Web UI Guide: WEB_UI_GUIDE.md
)
echo - Quick Start: QUICKSTART.md
echo - User Guide: USER_GUIDE.md
echo.
echo.

REM Offer to launch
if "%HAS_NODEJS%"=="true" (
    echo Choose interface:
    echo 1^) Web UI ^(modern, browser-based^)
    echo 2^) Desktop UI ^(PyQt, native^)
    echo 3^) Skip for now
    echo.
    set /p "choice=Enter choice (1-3): "
    
    if "!choice!"=="1" (
        echo.
        echo Launching Web UI...
        start cmd /k launch-web.bat
    ) else if "!choice!"=="2" (
        echo.
        echo Launching Desktop UI...
        start launch-desktop.bat
    ) else (
        echo.
        echo You can launch FileFlow anytime with launch-web.bat or launch-desktop.bat
    )
) else (
    set /p "launch=Would you like to launch the Desktop UI now? (Y/n): "
    if /i not "!launch!"=="n" (
        echo.
        echo Launching Desktop UI...
        start launch-desktop.bat
    )
)

echo.
echo Press any key to exit installer...
pause >nul
