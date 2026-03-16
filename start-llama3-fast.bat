@echo off
set "PATH=C:\Users\user\AppData\Roaming\npm;%PATH%"
node "%~dp0launcher.mjs" llama3.2:latest
echo.
echo Exit code: %ERRORLEVEL%
pause
