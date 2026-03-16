@echo off
REM Check Auto-Save Status

echo Git Auto-Save Status Check
echo ============================
echo.

REM Check if Auto-Save-Git.ps1 is running
tasklist /FI "IMAGENAME eq powershell.exe" /FO CSV | findstr /I "Auto-Save-Git.ps1" >nul
if %ERRORLEVEL% EQU 0 (
    echo [RUNNING] Auto-Save process is active
) else (
    echo [STOPPED] Auto-Save process is not running
)

echo.
echo Recent Auto-Save Log Entries:
echo ----------------------------
if exist "autosave.log" (
    powershell -Command "Get-Content autosave.log -Tail 10"
) else (
    echo No log file found
)

echo.
echo Press any key to view full log, or close to exit...
pause >nul
if exist "autosave.log" (
    notepad autosave.log
)
