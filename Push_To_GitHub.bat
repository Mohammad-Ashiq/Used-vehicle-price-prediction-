@echo off
title ReVahan - Push to GitHub for Cloud Deployment
cls
echo ======================================================================
echo             ReVahan - Uploading to Mohammad-Ashiq GitHub
echo ======================================================================
echo.
echo Target Repository:
echo   https://github.com/Mohammad-Ashiq/Used-vehicle-price-prediction-.git
echo.
echo GitHub now requires a Personal Access Token (or login) to push code.
echo.
echo If you have a GitHub Personal Access Token (starts with ghp_...):
echo   Paste it below and press Enter.
echo.
echo If you don't have a token:
echo   Just press Enter directly, and Git will prompt for your GitHub login.
echo.

set /p TOKEN="Enter Personal Access Token (optional, or press Enter): "

echo.
echo Configuring remote repository...
"C:\ReVahan_Project\tools\git\cmd\git.exe" remote remove origin >nul 2>&1

if "%TOKEN%"=="" (
    "C:\ReVahan_Project\tools\git\cmd\git.exe" remote add origin https://github.com/Mohammad-Ashiq/Used-vehicle-price-prediction-.git
) else (
    "C:\ReVahan_Project\tools\git\cmd\git.exe" remote add origin https://%TOKEN%@github.com/Mohammad-Ashiq/Used-vehicle-price-prediction-.git
)

"C:\ReVahan_Project\tools\git\cmd\git.exe" branch -M main

echo.
echo Pushing code and models to GitHub (this may take 15-30 seconds)...
"C:\ReVahan_Project\tools\git\cmd\git.exe" push -u origin main --force

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  SUCCESS! Your code is now live on GitHub:
    echo  https://github.com/Mohammad-Ashiq/Used-vehicle-price-prediction-
    echo.
    echo  Now go to https://dashboard.render.com
    echo  Click 'New +' -> 'Web Service' -> select your repo -> Name: revahan
    echo  And Render will launch: https://revahan.onrender.com !
    echo ======================================================================
) else (
    echo.
    echo [NOTE] If login failed, you can generate a free token at:
    echo        https://github.com/settings/tokens
    echo        (Check 'repo' box, generate, and paste it here).
)

echo.
pause
