@echo off
echo ========================================
echo Starting AI Donor Acquisition System
echo ========================================

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Flask application...
echo Application will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python src\main.py

