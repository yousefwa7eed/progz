@echo off
chcp 65001 >nul
title AlmajidApp - Public Access
color 0B

echo ========================================
echo   مؤسسة الماجد - الجهاز الإداري
echo ========================================
echo.

:: Kill old instances
taskkill /f /im python.exe 2>nul >nul
taskkill /f /im ssh.exe 2>nul >nul
timeout /t 2 /nobreak >nul

:: Start server
echo [1] Starting server on http://localhost:8500 ...
start "AlmajidApp-Server" /min python run_server.py
timeout /t 4 /nobreak >nul

:: Test server
echo [2] Verifying server...
curl -s http://localhost:8500 >nul 2>&1
if errorlevel 1 (
    echo     ERROR: Server did not start!
    pause
    exit /b 1
)
echo     Server is running.

:: Start tunnel
echo [3] Creating public URL via serveo.net ...
echo     (Stay connected - closing this window stops the tunnel)
echo.
start "AlmajidApp-Tunnel" /min cmd /c "ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8500 serveo.net 2>&1 | findstr /i "https://""
timeout /t 6 /nobreak >nul

:: Try to get the URL
echo.
echo ====================================================================
echo   Your public URL is shown in the "AlmajidApp-Tunnel" window
echo   (it looks like: https://xxxxx-xxxxx.serveousercontent.com)
echo ====================================================================
echo.
echo   Send this link to anyone to preview the app.
echo   The app is live as long as this window stays open.
echo.
echo   Close this window when done.
echo ====================================================================
echo.

:: Keep alive
:loop
timeout /t 30 /nobreak >nul
goto loop
