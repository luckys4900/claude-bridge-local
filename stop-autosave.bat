@echo off
REM Stop Git Auto-Save Process (safer version)

echo Stopping Git Auto-Save process...
echo.

REM Find PowerShell processes whose command line contains Auto-Save-Git.ps1
set "FOUND="
for /f "tokens=1 delims= " %%P in ('
  powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*Auto-Save-Git.ps1*' } | Select-Object -Expand ProcessId"
') do (
  echo Found Auto-Save process with PID %%P. Stopping...
  taskkill /F /PID %%P >nul 2>&1
  if not errorlevel 1 (
    set "FOUND=1"
  )
)

if "%FOUND%"=="1" (
  echo Auto-Save process stopped successfully.
) else (
  echo No Auto-Save process found or already stopped.
)

echo.
pause
