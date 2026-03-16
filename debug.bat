@echo off
set "NPM_BIN=C:\Users\user\AppData\Roaming\npm"
set "PATH=%NPM_BIN%;%PATH%"
set "LOG=%~dp0debug_log.txt"

echo === Claude Bridge Debug Log === > "%LOG%"
date /t >> "%LOG%"
time /t >> "%LOG%"
echo. >> "%LOG%"

echo [1] node version: >> "%LOG%"
node --version >> "%LOG%" 2>&1

echo [2] claude-bridge path: >> "%LOG%"
echo %NPM_BIN%\claude-bridge.cmd >> "%LOG%"

echo [3] Running claude-bridge... >> "%LOG%"
node "%NPM_BIN%\node_modules\@mariozechner\claude-bridge\dist\cli.js" openai llama3.2 --baseURL http://localhost:11434/v1 >> "%LOG%" 2>&1

echo [4] Exit code: %ERRORLEVEL% >> "%LOG%"
echo. >> "%LOG%"
echo === End === >> "%LOG%"

echo Log saved to: %LOG%
echo.
type "%LOG%"
pause
