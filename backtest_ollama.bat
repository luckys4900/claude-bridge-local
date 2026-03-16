@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Running Ollama backtest...
echo   Option 7: llama3.2:latest
echo   Option 8: qwen3:30b
echo   Option 9: qwen3:8b (was 7b - Ollama has 8b)
echo.
node backtest_ollama.mjs llama3.2:latest
echo.
pause
