@echo off
REM News Scraper Launcher
REM This batch file runs the news scraper application

echo ========================================
echo News Scraper - Starting...
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist "E:\Github\news.hungba.net-scraper\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call E:\Github\news.hungba.net-scraper\.venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at .venv\Scripts\activate.bat
    echo Running with system Python...
)

echo Running News Scraper...
echo.

REM Run the Python script
py run.py

REM Check if the script completed successfully
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Script encountered an error
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Script completed successfully!
    echo ========================================
)

echo.
echo Press any key to close this window...
pause >nul
