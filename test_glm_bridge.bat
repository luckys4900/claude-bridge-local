@echo off
set "PATH=C:\Users\user\AppData\Roaming\npm;%PATH%"
cd /d "%~dp0"

echo [TEST] GLM Bridge - Proxy + Claude Code (short prompt)
echo.
echo Starting proxy with glm-4.7-flashx...
echo.

node launcher.mjs glm glm-4.7-flashx -p "1+1=? Reply only the number."
echo.
echo Exit code: %ERRORLEVEL%
pause
