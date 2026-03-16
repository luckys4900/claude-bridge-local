@echo off
set "PATH=C:\Users\user\AppData\Roaming\npm;%PATH%"
node "%~dp0launcher.mjs" openrouter deepseek/deepseek-chat-v3-0324
echo.
echo Exit code: %ERRORLEVEL%
pause
