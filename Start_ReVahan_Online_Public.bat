@echo off
title ReVahan Live Public Online Server
cls
cd /d C:\ReVahan_Project
echo ======================================================================
echo          Starting ReVahan Server and Public Tunnel...
echo ======================================================================
echo.
python run_online_service.py
pause
