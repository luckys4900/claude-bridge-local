@echo off
REM Remove Auto-Save from Windows Startup

echo Removing Git Auto-Save from Windows Startup...
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP_FOLDER%\Git-Auto-Save.lnk"

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    if %ERRORLEVEL% EQU 0 (
        echo SUCCESS: Auto-Save removed from Windows Startup.
        echo Shortcut deleted: "%SHORTCUT%"
    ) else (
        echo ERROR: Failed to delete shortcut.
    )
) else (
    echo Auto-Save startup shortcut not found.
    echo It may have already been removed.
)

echo.
pause
