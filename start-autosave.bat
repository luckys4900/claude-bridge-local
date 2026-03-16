@echo off
REM Git Auto-Save Starter
REM This script starts the auto-save process in the background

echo Starting Git Auto-Save...
echo.
echo Press Ctrl+C to stop the auto-save process
echo.

REM Start PowerShell script with hidden window
start /min powershell -NoExit -ExecutionPolicy Bypass -File "Auto-Save-Git.ps1"

echo Auto-Save process started in background.
echo Check autosave.log for details.
echo.
pause
