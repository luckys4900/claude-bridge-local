@echo off
set "NPM_BIN=C:\Users\user\AppData\Roaming\npm"
set "CLAUDE_JS=%NPM_BIN%\node_modules\@anthropic-ai\claude-code\cli.js"
set "PATH=%NPM_BIN%;%PATH%"
set "ANTHROPIC_API_KEY=sk-ant-bridge-dummy"

echo [TEST] Running claude-bridge with llama3.2 non-interactive...
echo.

CALL "%NPM_BIN%\claude-bridge.cmd" openai llama3.2 --baseURL http://localhost:11434/v1 --claude-binary "%CLAUDE_JS%" --apiKey dummy -p "respond with only these words: BRIDGE_WORKING"

echo.
echo [RESULT] Exit code: %ERRORLEVEL%
pause
