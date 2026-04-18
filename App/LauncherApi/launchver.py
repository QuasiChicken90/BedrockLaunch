def launch(version):
    import os
    import re
    import subprocess
    import webbrowser
    from pathlib import Path
    import time

    launch.logs = ""

    def log(message):
        launch.logs += message + "\n"
        print(message)

    def run_logged(cmd, label=""):
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=isinstance(cmd, str)
        )
        if label:
            log(f"[{label}]")
        if result.stdout.strip():
            log(f"  stdout: {result.stdout.strip()}")
        if result.stderr.strip():
            log(f"  stderr: {result.stderr.strip()}")
        if result.returncode != 0:
            log(f"  WARNING: exited with code {result.returncode}")
        return result

    log(f"Setting up {version}...")
    match = re.search(r"(\d+\.\d+\.\d+)", version)
    if not match:
        log("Invalid version format.")
        return

    numeric_version = match.group(1)

    def parse_version(ver_str):
        return tuple(int(p) for p in ver_str.split("."))

    version_tuple = parse_version(numeric_version)
    threshold = parse_version("1.21.120")

    Path(f"launches/{version}").mkdir(parents=True, exist_ok=True)

    if version_tuple >= threshold:
        run_logged(
            'powershell.exe -Command "Get-AppxPackage -allusers *MinecraftWindows* | Remove-AppxPackage -allusers"',
            label="Remove MinecraftWindows"
        )
        path = f"Library/Installations/{version}/MinecraftBedrockGDK.msixvc"
        run_logged(
            ["powershell.exe", "-Command", f'Add-AppxPackage -Path "{path}"'],
            label="Install MSIXVC"
        )
    else:
        run_logged(
            'powershell.exe -Command "Get-AppxPackage -allusers *minecraftUWP* | Remove-AppxPackage -allusers"',
            label="Remove MinecraftUWP"
        )
        run_logged(
            f'powershell.exe Add-AppxPackage -Register "Library/Installations/{version}/AppXManifest.xml"',
            label="Register AppXManifest"
        )

    webbrowser.open("minecraft://")
    time.sleep(3)

    addons_dir = "Library/Addons"
    for dir_name in os.listdir(addons_dir):
        full_dir = os.path.join(addons_dir, dir_name)
        if os.path.isdir(full_dir):
            for pack_file, label in [("pack.mcpack", "mcpack"), ("pack.mcaddon", "mcaddon")]:
                pack_path = os.path.join(full_dir, pack_file)
                if os.path.isfile(pack_path):
                    run_logged(
                        ["powershell", "Start-Process", f'"{pack_path}"'],
                        label=f"Install {label}: {dir_name}"
                    )
                    time.sleep(3)

def get_launch_logs():
    return getattr(launch, "logs", "")
