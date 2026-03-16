@echo off
set "LOG=C:\Users\user\Desktop\claude-bridge-local\log2.txt"
set "NPM_BIN=C:\Users\user\AppData\Roaming\npm"
set "CLAUDE_JS=%NPM_BIN%\node_modules\@anthropic-ai\claude-code\cli.js"

echo [STEP1] bat started > "%LOG%"
echo NPM_BIN=%NPM_BIN% >> "%LOG%"
echo CLAUDE_JS=%CLAUDE_JS% >> "%LOG%"

echo [STEP2] checking files >> "%LOG%"
if exist "%NPM_BIN%\claude-bridge.cmd" (echo claude-bridge.cmd: OK >> "%LOG%") else (echo claude-bridge.cmd: MISSING >> "%LOG%")
if exist "%CLAUDE_JS%" (echo claude.js: OK >> "%LOG%") else (echo claude.js: MISSING >> "%LOG%")

echo [STEP3] running node directly >> "%LOG%"
node "%NPM_BIN%\node_modules\@mariozechner\claude-bridge\dist\cli.js" openai llama3.2 --baseURL http://localhost:11434/v1 --apiKey dummy --claude-binary "%CLAUDE_JS%" >> "%LOG%" 2>&1

echo [STEP4] exit code: %ERRORLEVEL% >> "%LOG%"

type "%LOG%"
pause
