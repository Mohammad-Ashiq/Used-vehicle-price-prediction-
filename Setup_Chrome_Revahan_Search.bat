@echo off
title Setup ReVahan in Chrome Search Bar
cls
echo ======================================================================
echo          ReVahan - Automatic Chrome Address Bar Shortcut Setup
echo ======================================================================
echo.
echo This tool configures Google Chrome so that whenever you type:
echo.
echo        revahan
echo.
echo into Chrome's address bar and hit Enter, it opens ReVahan immediately!
echo.
echo Note: Google Chrome must be closed for 3 seconds to update search shortcuts.
echo.

set /p userchoice="Would you like to close Chrome now and apply the shortcut? (Y/N): "
if /i "%userchoice%"=="Y" (
    echo Closing Chrome...
    taskkill /f /im chrome.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    python "C:\ReVahan_Project\add_chrome_keyword.py"
    echo.
    echo Re-launching Chrome...
    start chrome.exe
    echo.
    echo ======================================================================
    echo  SUCCESS! In Chrome's address bar, type:  revahan  and press Enter!
    echo ======================================================================
) else (
    echo.
    echo Skipping automatic injection.
    echo You can also install the ReVahan Chrome Extension from Desktop folder:
    echo "ReVahan_Chrome_Extension" in chrome://extensions !
)

echo.
pause
