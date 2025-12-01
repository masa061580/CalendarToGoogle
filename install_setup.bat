@echo off
setlocal EnableDelayedExpansion

echo ========================================================
echo  Calendar to Google Installer
echo ========================================================
echo.

:: 1. Check Python Installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found.
    echo Please install Python 3.10 or later from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo Python is installed.

:: 2. Install uv (Package Manager)
echo.
echo [2/5] Installing/Updating uv package manager...
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
if %errorlevel% neq 0 (
    echo Failed to install uv.
    pause
    exit /b 1
)

:: Refresh environment variables to use uv immediately
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"

:: 3. Sync Dependencies
echo.
echo [3/5] Installing dependencies...
cd /d "%~dp0"
uv sync
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Create Desktop Shortcut
echo.
echo [4/5] Creating Desktop shortcut...
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\CalendarToGoogle.lnk"
set "TARGET_PATH=%~dp0start.bat"
set "ICON_PATH=%~dp0calendar_to_google\resources\icon.ico" 

:: Create a temporary VBScript to create the shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut.vbs"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%temp%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut.vbs"
echo oLink.TargetPath = "%TARGET_PATH%" >> "%temp%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%temp%\CreateShortcut.vbs"
echo oLink.Description = "Calendar to Google" >> "%temp%\CreateShortcut.vbs"
echo oLink.Save >> "%temp%\CreateShortcut.vbs"

cscript //nologo "%temp%\CreateShortcut.vbs"
del "%temp%\CreateShortcut.vbs"
echo Shortcut created at %SHORTCUT_PATH%

:: 5. Setup Credentials
echo.
echo [5/5] Checking configuration...
if not exist "%USERPROFILE%\.calendar-to-google\credentials.json" (
    echo.
    echo [IMPORTANT] Google Calendar API credentials are required.
    echo Please place 'credentials.json' in:
    echo %USERPROFILE%\.calendar-to-google\
    echo.
    echo You can also register it from the app menu later.
)

echo.
echo ========================================================
echo  Installation Complete!
echo ========================================================
echo.
echo You can start the app from the Desktop shortcut.
echo.
pause
