import os
import ctypes
import sys
import subprocess
import winreg

import requests

def prepare():
    createData = ['Instances', 'Config/Logs', 'Config/Temp']
    for folder in createData:
        if not os.path.exists(folder):
            os.makedirs(folder)

def startGui():
    import subprocess
    path = os.path.join(os.getcwd(), 'Launcher', 'Resources', 'Bin', 'gui_wv.exe')
    if os.path.exists(path):
        subprocess.Popen([path])

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def adminPerms():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

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


def opendir(path):
    if os.path.exists(path):
        subprocess.Popen(f'explorer.exe "{path}"')

def get_storage_used():
    total_size = 0
    for dirpath, dirnames, filenames in os.walk("Instances"):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size


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