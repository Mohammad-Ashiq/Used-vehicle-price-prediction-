@echo off
title ReVahan - Push to GitHub for Cloud Deployment
cls
echo ======================================================================
echo             ReVahan - Connect to GitHub for 24/7 Cloud Deploy
echo ======================================================================
echo.
echo Your local Git repository is initialized and committed with all files:
echo   - 4 Trained ML Models (Cars, Bikes, Lorries, Autos)
echo   - Full Indian Datasets (70+ brands, 400+ models, 36 states)
echo   - Progressive Web App (PWA) configuration
echo   - Dockerfile, Procfile, render.yaml
echo.
echo Step 1: Create a new repository on GitHub:
echo         Open: https://github.com/new
echo         Name it: revahan  (Keep it Public or Private)
echo.
echo Step 2: Paste your GitHub repository URL below
echo         (e.g., https://github.com/yourusername/revahan.git)
echo.
set /p REPO_URL="Enter your GitHub Repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered. Exiting...
    pause
    exit /b
)

echo.
echo Connecting to GitHub repository...
"C:\ReVahan_Project\tools\git\cmd\git.exe" remote remove origin >nul 2>&1
"C:\ReVahan_Project\tools\git\cmd\git.exe" remote add origin %REPO_URL%
"C:\ReVahan_Project\tools\git\cmd\git.exe" branch -M main

echo.
echo Pushing code to GitHub...
"C:\ReVahan_Project\tools\git\cmd\git.exe" push -u origin main

echo.
echo ======================================================================
echo  Code uploaded to GitHub!
echo  Now go to https://dashboard.render.com/select-repo?type=web
echo  and select your 'revahan' repository to deploy in 1-click!
echo ======================================================================
echo.
pause
