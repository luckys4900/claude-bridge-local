@echo off
REM Stop Git Auto-Save Process

echo Stopping Git Auto-Save process...
echo.

REM Find and kill PowerShell processes running Auto-Save-Git.ps1
taskkill /F /FI "WINDOWTITLE eq Auto-Save*" 2>nul
taskkill /F /IM powershell.exe /FI "IMAGENAME eq powershell.exe" 2>nul | findstr "SUCCESS" >nul

if %ERRORLEVEL% EQU 0 (
    echo Auto-Save process stopped successfully.
) else (
    echo No Auto-Save process found or already stopped.
)

echo.
pause
