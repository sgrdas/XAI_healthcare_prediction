@echo off
title Explainable AI Health Framework Launcher
color 0A

echo ================================================================
echo   Explainable AI Framework for Lifestyle Disease Prediction
echo ================================================================
echo.
echo [*] Launching application at http://127.0.0.1:5000 ...
echo [*] Admin Credentials: admin@healthai.com  ^|  Admin@1234
echo [*] Press Ctrl+C in this terminal to stop the server.
echo ================================================================
echo.

:: Open browser
start "" "http://127.0.0.1:5000"

:: Navigate to project directory and run app
cd /d "%~dp0Major_project-main"
python app.py

pause
