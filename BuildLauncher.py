import os
import shutil
from time import sleep

version = "Beta_2"

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
    
def renameFile(old, new):
    os.rename(old, new)
    log(f"Renamed file: {old} -> {new}")

if os.path.isdir("buildexec"):
    shutil.rmtree("buildexec")

def removePycache(pathtree):
    for root, dirs, _ in os.walk(pathtree):
        for dirname in dirs:
            if dirname == "__pycache__":
                full_path = os.path.join(root, dirname)
                print(f"Removed pycache: {full_path}")
                shutil.rmtree(full_path)

run("pip install -r requirements.txt")

run("mkdir buildexec")

icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Resources", "BedrockLaunch.ico")

run("pyinstaller Launcher.py --clean --workpath buildexec/temp --distpath buildexec/exe --specpath buildexec/temp --noconfirm --noconsole --icon " + icon_path)

mkdir("buildexec/exe/Launcher/launches")

copydir("Config", "buildexec/exe/Launcher/_internal/Config")
copydir("App", "buildexec/exe/Launcher/_internal/App")
copydir("App", "buildexec/exe/Launcher/App")

mkdir("buildexec/exe/Launcher/Library/Installations")
mkdir("buildexec/exe/Launcher/_internal/UAC")

deletedir("buildexec/exe/Launcher/App/Themes/")

deletefile("buildexec/exe/Launcher/_internal/App/selected.txt")

# delay renaming so it wont give a "file in use" error randomly
sleep(3)

renameFile("buildexec/exe/Launcher/Launcher.exe", f"buildexec/exe/Launcher/BedrockLaunch-{version}.exe")

removePycache("buildexec/exe/Launcher")

log("Complete.")
