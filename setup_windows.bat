@echo off
echo ========================================
echo AI Donor Acquisition System - Windows Setup
echo ========================================

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install flask flask-cors scikit-learn openai beautifulsoup4 requests sqlalchemy flask-sqlalchemy python-dotenv

echo Generating requirements.txt...
pip freeze > requirements.txt

echo Creating .env file from template...
if not exist ".env" (
    copy ".env.example" ".env"
    echo .env file created from template. Please edit it with your API keys.
) else (
    echo .env file already exists.
)

echo Creating logs directory...
if not exist "logs" mkdir logs

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo IMPORTANT: Edit the .env file with your OpenAI API key!
echo.
echo To start the application:
echo 1. Open VS Code in this directory
echo 2. Run: run_windows.bat
echo    OR
echo    Run: venv\Scripts\activate.bat
echo    Then: python src\main.py
echo.
echo The application will be available at: http://localhost:5000
echo ========================================

pause

