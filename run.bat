@echo off
REM Exam Mark Prediction System - Windows Startup Script

echo.
echo ============================================
echo Exam Mark Prediction System
echo ============================================
echo.

REM Check for Python and create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    set PYTHON_CMD=python
    python --version >nul 2>&1
    if errorlevel 1 (
        set PYTHON_CMD=python3
        python3 --version >nul 2>&1
        if errorlevel 1 (
            set PYTHON_CMD=py
            py --version >nul 2>&1
            if errorlevel 1 (
                echo ERROR: Python not found! Please install Python and add it to your PATH.
                pause
                exit /b 1
            )
        )
    )
    echo Using %PYTHON_CMD% to create venv...
    %PYTHON_CMD% -m venv venv
)


REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if port 5000 is already in use
netstat -ano | findstr :5000 > nul
if %errorlevel% == 0 (
    echo.
    echo WARNING: Port 5000 is already in use! 
    echo This might be a previous instance of the app.
    echo Please close any other terminal windows running the app.
    echo.
)

REM Run Flask app
echo.
echo ============================================
echo Starting Flask application...
echo Application will be available at: http://localhost:5000
echo.
echo NOTE: If the browser doesn't open automatically, 
echo please go to http://localhost:5000 manually.
echo ============================================
echo.

REM Start the browser after a short delay (using ping for compatibility)
start /b cmd /c "ping 127.0.0.1 -n 6 >nul && start http://localhost:5000"

REM Run the app (this blocks)
"%~dp0venv\Scripts\python.exe" backend\app.py

if errorlevel 1 (
    echo.
    echo ERROR: The application failed to start.
    echo Please check the error message above.
    pause
)

pause

