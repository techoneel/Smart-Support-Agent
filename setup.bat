@echo off
echo Setting up Smart Support Agent development environment...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Please install Python 3.9+ from https://www.python.org/downloads/
    exit /b 1
)

:: Check if virtual environment exists and remove if it does
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -e .
pip install -e ".[test]"

:: Create data directories
echo Creating data directories...
mkdir data 2>nul
mkdir logs 2>nul

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env with your API keys and configuration
)

echo Setup complete! Activate the virtual environment with:
echo venv\Scripts\activate