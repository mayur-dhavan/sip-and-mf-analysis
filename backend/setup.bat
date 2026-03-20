@echo off
REM Setup script for Windows

echo Setting up Mutual Fund Volatility Analyzer Backend...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verify setup
echo.
echo Verifying setup...
python setup.py

echo.
echo Setup complete!
echo To activate the virtual environment, run: venv\Scripts\activate
echo To start the server, run: uvicorn app.main:app --reload
