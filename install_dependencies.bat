@echo off
echo ===================================
echo SELO FileFlow - Setup Dependencies
echo ===================================
echo.

echo Installing required Python packages...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Checking for development tools...

where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo NSIS (Nullsoft Scriptable Install System) not found.
    echo If you want to build Windows installers, please install NSIS from:
    echo https://nsis.sourceforge.io/
    echo.
    echo After installation, make sure to add it to your PATH.
) else (
    echo NSIS found. You can build installers with build_installer.py
)

echo.
echo Dependencies installation complete!
echo.
echo You can now:
echo 1. Run the application with: python run_organizer.py --ui
echo 2. Build a standalone executable with: python build_installer.py
echo.

pause
