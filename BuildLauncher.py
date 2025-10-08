import os
import shutil
def run(command):
    os.system(command)

def mkdir(path):
    os.makedirs(path, exist_ok=True)
def copydir(src, dest):
    shutil.copytree(src, dest, dirs_exist_ok=True)

if os.path.isdir("buildexec"):
    shutil.rmtree("buildexec")

run("pip install -r requirements.txt")

run("mkdir buildexec")

run("pyinstaller Launcher.py --clean --workpath buildexec/temp --distpath buildexec/exe --specpath buildexec/temp --noconfirm --noconsole")

mkdir("buildexec/exe/Launcher/launches")

copydir("Config", "buildexec/exe/Launcher/_internal/Config")
copydir("App", "buildexec/exe/Launcher/_internal/App")
copydir("App", "buildexec/exe/Launcher/App")

mkdir("buildexec/exe/Launcher/Library/Installations")
mkdir("buildexec/exe/Launcher/_internal/UAC")
