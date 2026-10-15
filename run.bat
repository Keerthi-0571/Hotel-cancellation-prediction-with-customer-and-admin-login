@echo off
setlocal
cd /d "%~dp0"
title Hotel Cancellation Prediction - Setup

echo ================================================
echo   Hotel Cancellation Prediction
echo ================================================
echo.

rem ---------- 1. find Python ----------
set "PY="
py -3.14 --version >nul 2>&1 && set "PY=py -3.14"
if not defined PY ( py -3 --version >nul 2>&1 && set "PY=py -3" )
if not defined PY ( python --version >nul 2>&1 && set "PY=python" )

if not defined PY (
    echo Python was not found on this computer.
    echo Install Python 3.12 or newer from https://www.python.org/downloads/
    echo During install, tick "Add python.exe to PATH". Then run this file again.
    pause
    exit /b 1
)

rem ---------- 2. create the virtual environment (first run only) ----------
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY% -m venv venv
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

rem ---------- 3. install packages (first run only) ----------
if not exist "venv\.deps_installed" (
    echo Installing packages. This needs internet and takes a few minutes...
    "venv\Scripts\python.exe" -m pip install --upgrade pip
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Package install failed. Check your internet connection.
        echo If the error mentions scikit-learn 1.9.0 or numpy 2.5.2, your Python is
        echo too old: install Python 3.12 or newer, delete the "venv" folder, run again.
        pause
        exit /b 1
    )
    echo done> "venv\.deps_installed"
)

rem ---------- 4. start backend + website ----------
echo Starting the backend...
start "Hotel API (backend) - keep this window open" /D "%~dp0backend" cmd /k ""%~dp0venv\Scripts\python.exe" app.py"

echo Starting the website...
start "Hotel website (frontend) - keep this window open" /D "%~dp0." cmd /k ""%~dp0venv\Scripts\python.exe" -m http.server 5500 --bind 127.0.0.1"

timeout /t 6 /nobreak >nul
start "" "http://127.0.0.1:5500/frontend/login.html"

echo.
echo The website should open in your browser.
echo   Customer login : http://127.0.0.1:5500/frontend/login.html
echo   Admin login    : http://127.0.0.1:5500/frontend/admin_login.html
echo.
echo To stop the project, close the two black windows that opened.
pause
