@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Tao virtual environment...
    py -m venv .venv
)

echo [2/3] Cai / cap nhat thu vien...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Cai thu vien that bai. Kiem tra Python va Internet.
    pause
    exit /b 1
)

echo [3/3] Chay AutoTest...
".venv\Scripts\python.exe" main.py

pause
