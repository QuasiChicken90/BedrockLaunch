@echo off
timeout /t 5 /nobreak >nul

powershell -Command "Expand-Archive -Force 'update.zip' '.'"

del /f /q "update.zip"
del /f /q "%~dp0\App\welcome.txt"

start "" "Launcher.exe"

exit
