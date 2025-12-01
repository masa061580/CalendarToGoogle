@echo off
chcp 65001 > nul
echo ========================================
echo  Calendar to Google - Startup Setup
echo ========================================
echo.

set "APP_DIR=%~dp0"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_PATH=%STARTUP_FOLDER%\CalendarToGoogle.vbs"

echo App directory: %APP_DIR%
echo.
echo Creating startup script...

:: Create VBS launcher with proper path handling
    echo On Error Resume Next
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo Set FSO = CreateObject^("Scripting.FileSystemObject"^)
    echo.
    echo AppDir = "%APP_DIR:~0,-1%"
    echo PythonExe = AppDir ^& "\.venv\Scripts\pythonw.exe"
    echo LauncherScript = AppDir ^& "\calendar_to_google\launcher.py"
    echo.
    echo If FSO.FileExists^(PythonExe^) Then
    echo     WshShell.CurrentDirectory = AppDir
    echo     WshShell.Run """" ^& PythonExe ^& """ """ ^& LauncherScript ^& """", 0, False
    echo Else
    echo     MsgBox "Python not found in .venv. Please run install_setup.bat first.", vbCritical, "Calendar to Google"
    echo End If
)

if exist "%VBS_PATH%" (
    echo.
    echo [OK] Startup script created!
    echo.
    echo Location: %VBS_PATH%
    echo.
    echo Testing startup script now...
    echo.
    cscript //nologo "%VBS_PATH%"
    echo.
    echo If no error appeared, check system tray for the calendar icon.
    echo.
    echo The app will start automatically when Windows starts.
) else (
    echo.
    echo [ERROR] Failed to create startup script.
)

echo.
pause
