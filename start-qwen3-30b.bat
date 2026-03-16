@echo off
set "PATH=C:\Users\user\AppData\Roaming\npm;%PATH%"
node "%~dp0launcher.mjs" qwen3:30b
echo.
echo Exit code: %ERRORLEVEL%
pause
