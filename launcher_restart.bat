@echo off
setlocal

taskkill /IM neu_wv.exe /F /T >nul 2>&1
taskkill /IM launcher.exe /F /T >nul

timeout /t 2 /nobreak >nul

tar -xf update.zip

del /f /q "update.zip"
del /f /q "%~dp0\App\welcome.txt"

start "Launcher.exe"

exit
