@echo off
title BedrockLaunch Updating...

taskkill /F /IM Launcher.exe 2>nul
taskkill /F /IM neu_wv.exe 2>nul

timeout /t 2 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Expand-Archive -Path 'update.zip' -DestinationPath '.' -Force; if (Test-Path 'App\welcome.txt') { Remove-Item 'App\welcome.txt' -Force }; Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Update complete! Please open Launcher.exe to continue.', 'Update Installed', 'OK', 'Information')"

exit
