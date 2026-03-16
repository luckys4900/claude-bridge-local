@echo off
chcp 65001 >nul
set "PATH=C:\Users\user\AppData\Roaming\npm;%PATH%"
echo.
echo ============================================
echo   Claude Bridge - Model Select
echo ============================================
echo.
echo  [OpenRouter - Cloud]
echo   1) DeepSeek V3     ~$0.27/M  (recommended)
echo   2) Qwen3 235B      ~$0.13/M  (cheapest)
echo   3) Claude Haiku    ~$0.80/M  (Claude compat)
echo.
echo  [GLM - Z.ai Coding Plan]
echo   4) GLM-4.7         (flagship)
echo   5) GLM-4.7-FlashX  (lightweight/fast)
echo   6) GLM-4.7-Flash   (Coding Plan unlimited, recommended)
echo.
echo  [Ollama - Local GPU, free]
echo   7) Llama3.2        2GB
echo   8) Qwen3 30B       18GB
echo   9) Qwen3 8B        5GB
echo.
set /p choice=Enter number (1-9):

REM Trim spaces from choice
set "choice=%choice: =%"

if "%choice%"=="1" node "%~dp0launcher.mjs" openrouter deepseek/deepseek-chat-v3-0324
if "%choice%"=="2" node "%~dp0launcher.mjs" openrouter qwen/qwen3-235b-a22b
if "%choice%"=="3" node "%~dp0launcher.mjs" openrouter anthropic/claude-haiku-4-5-20251001
if "%choice%"=="4" node "%~dp0launcher.mjs" glm glm-4.7
if "%choice%"=="5" node "%~dp0launcher.mjs" glm glm-4.7-flashx
if "%choice%"=="6" node "%~dp0launcher.mjs" glm glm-4.7-flash

if "%choice%"=="7" node "%~dp0launcher.mjs" ollama llama3.2:latest
if "%choice%"=="8" node "%~dp0launcher.mjs" ollama qwen3:30b
if "%choice%"=="9" node "%~dp0launcher.mjs" ollama qwen3:8b

if not "%choice%"=="1" if not "%choice%"=="2" if not "%choice%"=="3" if not "%choice%"=="4" if not "%choice%"=="5" if not "%choice%"=="6" if not "%choice%"=="7" if not "%choice%"=="8" if not "%choice%"=="9" (
  echo Invalid choice: [%choice%]. Enter 1-9.
  pause
  exit /b 1
)

echo.
echo Exit code: %ERRORLEVEL%
pause

