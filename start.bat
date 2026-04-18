@echo off
title ✨ SocialSpark - DBMS Project
color 0D
echo.
echo  ============================================
echo   ✨ SocialSpark - Social Media DBMS App
echo   Built with Python + SQLite (No JS needed)
echo  ============================================
echo.
echo  [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python not found! Please install Python 3.x
    echo  [!] Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  [OK] Python found!
echo.
echo  [*] Starting SocialSpark server...
echo  [*] Opening browser at http://localhost:8080
echo.
echo  Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
python app.py
pause
