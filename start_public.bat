@echo off
chcp 65001 >nul
title AlmajidApp - Server
echo ========================================
echo   مؤسسة الماجد - الجهاز الإداري
echo   Server at http://localhost:8500
echo ========================================
echo.
echo Starting server...
start "AlmajidApp-Server" cmd /c "python run_server.py"
timeout /t 3 /nobreak >nul
echo.
echo Now creating public tunnel...
echo You will see a URL like: https://xxxx.localhost.run
echo Send that URL to the buyer.
echo.
echo Close this window to stop the tunnel.
echo ========================================
ssh -o StrictHostKeyChecking=no -R 80:localhost:8500 nokey@localhost.run
pause
