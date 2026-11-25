@echo off
title ReVahan - AI Used Vehicle Price Prediction System
cd /d "%~dp0"
echo ================================================================
echo         ReVahan - Used Vehicle Price Prediction System
echo ================================================================
echo [1/2] Launching Web Browser at http://127.0.0.1:5000 ...
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"
echo [2/2] Starting Flask Backend Server (Port 5000)...
".venv\Scripts\python.exe" app.py
pause
