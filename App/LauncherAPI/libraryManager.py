import os
import requests
import shutil
from contextlib import contextmanager
from .versions import Versions

@contextmanager
def change_dir(destination):
    prev_dir = os.getcwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(prev_dir)

def createInstance(version):
    print('Creating...')
    installver = Versions.get_by_version(version)

    if not installver:
        print(f"Version {version} not found.")
        return False

    print(f"Downloading from: {installver.uri}")

    current_dir = os.getcwd()
    new_working_dir = os.path.join(current_dir, "Library", "Installations", version)
    os.makedirs(new_working_dir, exist_ok=True)

    zip_path = os.path.join(new_working_dir, f"{version}.zip")

    try:
        with requests.get(installver.uri, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as file:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
    except Exception as e:
        print(f"Download failed: {e}")
        return False

    with change_dir(new_working_dir):
        print("Download complete. Extracting...")
        try:
            shutil.unpack_archive(zip_path, extract_dir=new_working_dir)
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False

        print("Extraction complete. Cleaning up...")
        try:
            os.remove(zip_path)
        except FileNotFoundError:
            pass

        for filename in ["AppxSignature.p7x", "[Content_Types].xml", "AppxBlockMap.xml"]:
            if os.path.exists(filename):
                os.remove(filename)

        if os.path.exists("AppxMetadata"):
            shutil.rmtree("AppxMetadata")

    print(f"Instance {version} created successfully.")
    return True


def getInstances():
    path = "Library/Installations"
    for thing in os.listdir(path):
        item_path = os.path.join(path, thing)
        if os.path.isdir(item_path) and not os.listdir(item_path):
            os.rmdir(item_path)
    return os.listdir(path)

def deleteInstance(instanceName):
    instancePath = os.path.join("Library", "Installations", instanceName)
    if os.path.exists(instancePath) and os.path.isdir(instancePath):
        shutil.rmtree(instancePath)
        return True
    return False

def setInstance(instanceName):
    selectedPath = os.path.join("App", "selected.txt")
    with open(selectedPath, "w") as f:
        f.write(instanceName)
    return True