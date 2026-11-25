@echo off
title ReVahan - System Domain Register

:: Check for Administrator privileges, auto-elevate if needed
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator permissions to register revahan domain...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~fn0\"' -Verb RunAs"
    exit /b
)

echo ========================================================
echo    Registering 'revahan.in' and 'www.revahan.in' in Hosts
echo ========================================================
echo.

set HOSTS=%windir%\system32\drivers\etc\hosts

:: Check if revahan.in already exists
findstr /i "revahan.in" "%HOSTS%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] 'revahan.in' is already registered in your Windows hosts file!
) else (
    echo Adding 127.0.0.1 revahan.in to hosts...
    echo. >> "%HOSTS%"
    echo # ReVahan Local Domain Mapping >> "%HOSTS%"
    echo 127.0.0.1   revahan >> "%HOSTS%"
    echo 127.0.0.1   revahan.in >> "%HOSTS%"
    echo 127.0.0.1   www.revahan.in >> "%HOSTS%"
    echo 127.0.0.1   revahan.com >> "%HOSTS%"
    echo 127.0.0.1   www.revahan.com >> "%HOSTS%"
    echo [SUCCESS] Domains added to hosts!
)

:: Flush DNS
echo Flushing Windows DNS Cache...
ipconfig /flushdns >nul

echo.
echo ========================================================
echo   NOW IN ANY BROWSER (Chrome, Edge, Firefox, Brave):
echo   You can type:
echo     http://www.revahan.in:5000
echo     http://revahan.in:5000
echo ========================================================
echo.
pause
