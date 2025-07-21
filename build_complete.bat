@echo off
echo Building SELO FileFlow...
python build_app.py > build_log.txt 2>&1
echo Build completed. See build_log.txt for details.
echo.
echo Creating installer...
python create_fileflow_installer.py >> build_log.txt 2>&1
echo Done!
