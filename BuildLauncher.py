import os
import shutil
import subprocess

def log(text):
    print(f"LOG: {text}")

def run(command):
    os.system(command)
    log(f"Ran command: {command}")

def mkdir(path):
    os.makedirs(path, exist_ok=True)
    log(f"Created directory: {path}")

def copydir(src, dest):    
    shutil.copytree(src, dest, dirs_exist_ok=True)
    log(f"Copied directory: {src} -> {dest}")

def deletefile(path):
    os.remove(path)
    log(f"Deleted file: {path}")

def deletedir(path):
    shutil.rmtree(path)
    log(f"Deleted directory: {path}")
    
def renamefile(old, new):
    os.rename(old, new)
    log(f"Renamed file: {old} -> {new}")

def copyfile(src, dest):
    shutil.copy2(src, dest)
    log(f"Copied file: {src} -> {dest}")

if os.path.isdir("buildexec"):
    shutil.rmtree("buildexec")

run("pip install -r requirements.txt")

subprocess.run([
    "pyinstaller",
    "Launcher.py",
    "--clean",
    "--workpath", "buildexec/temp",
    "--distpath", "buildexec/exe",
    "--specpath", "buildexec/temp",
    "--noconfirm"
], check=True)

os.chdir("GUI/BedrockLaunch")

run("npm install")

os.chdir("src-tauri")

run("cargo build --release")

os.chdir("../../../")

copyfile("GUI/BedrockLaunch/src-tauri/target/release/bedrocklaunch.exe", "buildexec/exe/Launcher/bedrocklaunch.exe")

renamefile("buildexec/exe/Launcher/Launcher.exe", "buildexec/exe/Launcher/backend.exe")

copydir("Launcher", "buildexec/exe/Launcher/_internal/Launcher")

copyfile("launcher_restart.bat", "buildexec/exe/Launcher/launcher_restart.bat")
