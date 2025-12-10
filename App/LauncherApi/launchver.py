
import subprocess

def launch(version):
    import os
    import re
    import webbrowser
    from pathlib import Path
    import time

    print(f"Setting up {version}...")

    match = re.search(r"(\d+\.\d+\.\d+)", version)
    if not match:
        print("Invalid version format.")
        return
    numeric_version = match.group(1)

    def parse_version(ver_str):
        parts = ver_str.split(".")
        return tuple(int(p) for p in parts)

    version_tuple = parse_version(numeric_version)
    threshold = parse_version("1.21.120")

    Path(f"launches/{version}").mkdir(parents=True, exist_ok=True)

    if version_tuple >= threshold:
        os.system(f'powershell.exe -Command "Get-AppxPackage -allusers *MinecraftWindows* | Remove-AppxPackage -allusers"')
        path = f"Library/Installations/{version}/MinecraftBedrockGDK.msixvc"

        subprocess.run([
            "powershell.exe",
            "-Command",
            f'Add-AppxPackage -Path "{path}"'
        ])
        webbrowser.open("minecraft://")
    else:
        os.system(f'powershell.exe -Command "Get-AppxPackage -allusers *minecraftUWP* | Remove-AppxPackage -allusers"')
        os.system(f'powershell.exe Add-AppxPackage -Register "Library/Installations/{version}/AppXManifest.xml"')
        webbrowser.open("minecraft://")

    time.sleep(3)
    
    addons_dir = "Library/Addons"

    for dir_name in os.listdir(addons_dir):
        full_dir = os.path.join(addons_dir, dir_name)

        if os.path.isdir(full_dir):
            mcpack = os.path.join(full_dir, "pack.mcpack")
            mcaddon = os.path.join(full_dir, "pack.mcaddon")

            if os.path.isfile(mcpack):
                subprocess.Popen(["powershell", "Start-Process", f'"{mcpack}"'], shell=True)
                time.sleep(3)

            if os.path.isfile(mcaddon):
                subprocess.Popen(["powershell", "Start-Process", f'"{mcaddon}"'], shell=True)
                time.sleep(3)

    
