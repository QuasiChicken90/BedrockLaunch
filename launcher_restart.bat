@echo off
title BedrockLaunch Updating...

taskkill /F /IM BedrockLaunch.exe 2>nul

taskkill /F /IM Backend.exe 2>nul

timeout /t 2 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Expand-Archive -Path 'update.zip' -DestinationPath '.' -Force; Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Update complete! Please open BedrockLaunch.exe to continue.', 'Update Installed', 'OK', 'Information')"

exit
