@echo off
REM Stock Analysis API Startup Script for Windows

echo ========================================
echo Stock Analysis API - Startup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your ANTHROPIC_API_KEY
    echo to enable advanced LLM analysis features.
    echo.
    pause
)

REM Install dependencies
echo Installing/updating dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo Starting Stock Analysis API...
echo ========================================
echo.

REM Start the server
python run.py

pause
