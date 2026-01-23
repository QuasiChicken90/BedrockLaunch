progress = 0
import requests
import subprocess
import os
import winreg

def fetchUpdate(updateURL):
    global progress

    progress = 10
    print("Downloading from:", updateURL)

    response = requests.get(updateURL, allow_redirects=True, stream=True)
    print("Status:", response.status_code)
    print("Final URL:", response.url)

    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}\n{response.text[:200]}")

    progress = 30
    with open("update.zip", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    progress = 100


def getUpdateProgress():
    global progress
    return progress

import subprocess

def check_developer_mode():
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        'if ((Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AppModelUnlock" '
        '-Name AllowDevelopmentWithoutDevLicense -ErrorAction SilentlyContinue)'
        '.AllowDevelopmentWithoutDevLicense -eq 1) { "yes" } else { "no" }'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().lower() == "yes"

def enable_developer_mode():
    with winreg.CreateKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    ) as key:
        winreg.SetValueEx(key, "AllowDevelopmentWithoutDevLicense", 0, winreg.REG_DWORD, 1)
