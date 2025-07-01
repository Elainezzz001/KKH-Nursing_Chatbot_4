@echo off
echo Starting KKH Nursing Chatbot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade requirements
echo Installing/updating dependencies...
pip install -r requirements.txt

REM Check if LM Studio is running (optional)
echo.
echo NOTE: Make sure LM Studio is running with OpenHermes model loaded
echo       on localhost:1234 for full functionality
echo.

REM Start the application
echo Starting Streamlit application...
streamlit run app.py

pause
