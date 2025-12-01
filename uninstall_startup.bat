@echo off
chcp 65001 > nul
echo ========================================
echo  Calendar to Google - Remove Startup
echo ========================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_PATH=%STARTUP_FOLDER%\CalendarToGoogle.vbs"

if exist "%VBS_PATH%" (
    del "%VBS_PATH%"
    echo [OK] Startup script removed.
    echo.
    echo The app will no longer start automatically.
) else (
    echo [INFO] Startup script not found. Nothing to remove.
)

echo.
pause
