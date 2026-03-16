@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ===== GLM4.7 API バックテスト =====
echo.
node backtest_glm.mjs
echo.
echo Exit: %ERRORLEVEL%
pause
