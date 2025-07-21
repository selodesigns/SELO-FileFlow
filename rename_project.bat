@echo off
echo ===================================
echo SELO FileFlow - Directory Renaming
echo ===================================
echo.
echo This script will rename the project directory from 'downloadorganizer' to 'SELO-FileFlow'
echo.
echo Please close any open files or applications that might be using files in this directory.
echo.
pause

set PARENT_DIR=%~dp0..
set OLD_PATH=%~dp0
set NEW_PATH=%PARENT_DIR%\SELO-FileFlow

echo.
echo Moving files from:
echo %OLD_PATH%
echo To:
echo %NEW_PATH%
echo.

if exist "%NEW_PATH%" (
    echo ERROR: Destination directory already exists.
    echo Please remove it first or choose a different name.
    goto end
)

mkdir "%NEW_PATH%"
xcopy "%OLD_PATH%*.*" "%NEW_PATH%" /E /H /C /I
if %errorlevel% neq 0 (
    echo Failed to copy files. Aborting.
    goto end
)

echo.
echo Directory renamed successfully!
echo.
echo Now you can:
echo 1. Delete the old directory (after ensuring everything was copied correctly)
echo 2. Navigate to the new directory at: %NEW_PATH%
echo 3. Run the install_dependencies.bat script to set up the development environment
echo.

:end
pause
