@echo off
REM Install Auto-Save to Windows Startup

echo Installing Git Auto-Save to Windows Startup...
echo.

REM Get the absolute path of the script
set "SCRIPT_DIR=%~dp0"
set "HIDDEN_SCRIPT=%SCRIPT_DIR%start-autosave-hidden.bat"

REM Check if the script exists
if not exist "%HIDDEN_SCRIPT%" (
    echo ERROR: %HIDDEN_SCRIPT% not found!
    echo Please ensure you are running this script from the project directory.
    pause
    exit /b 1
)

REM Get Startup folder path
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create shortcut
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_FOLDER%\Git-Auto-Save.lnk'); $s.TargetPath = '%HIDDEN_SCRIPT%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Auto-Save added to Windows Startup.
    echo Shortcut created: "%STARTUP_FOLDER%\Git-Auto-Save.lnk"
    echo.
    echo Auto-Save will start automatically when you log in to Windows.
    echo.
    echo To remove it, delete the shortcut: "%STARTUP_FOLDER%\Git-Auto-Save.lnk"
) else (
    echo ERROR: Failed to create startup shortcut.
)

echo.
pause
