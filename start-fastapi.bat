@echo off
echo FastAPI Memory Server Starting...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main.py
