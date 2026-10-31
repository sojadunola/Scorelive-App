@echo off
title ScorePulse - Live Sport Score App
echo ========================================================
echo        Starting ScorePulse - Live Sport Score App       
echo ========================================================
echo.

:: Detect Python executable
set "PY_CMD=python"
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        echo [ERROR] Python not found. Please ensure Python 3.12 is installed.
        pause
        exit /b 1
    )
)

echo [INFO] Using Python: %PY_CMD%
echo [INFO] Launching ScorePulse Web Server...
echo [INFO] Opening browser at http://127.0.0.1:5000
echo.

:: Launch browser after 1.5 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Start the Flask web application
"%PY_CMD%" app.py

pause
