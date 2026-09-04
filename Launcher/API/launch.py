def launch(version):
    import os
    import re
    import subprocess
    import webbrowser
    import time
    import requests
    from pathlib import Path
    from .installer.Versions import Versions
    import shutil

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

    instance_path = Path(f"Instances/{version}")
    instance_path.mkdir(parents=True, exist_ok=True)

    if version_tuple >= threshold:

        msix_path = instance_path / "MinecraftBedrockGDK.msixvc"

        if not msix_path.exists():

            log(f"{msix_path} not found.")
            log(f"Downloading {version}...this can take a while")

            gdkverslink = (
                "https://raw.githubusercontent.com/"
                "LukasPAH/minecraft-windows-gdk-version-db/"
                "refs/heads/main/historical_versions.json"
            )

            try:
                response = requests.get(gdkverslink, timeout=15)
                response.raise_for_status()
                data = response.json()

                final_url = None
                
                for entry in data.get("releaseVersions", []):

                    entry_version = entry["version"].replace(
                        "Release ", ""
                    )

                    if entry_version == version:
                        final_url = entry["urls"][0]
                        break

                if not final_url:
                    log(f"GDK URL for {version} not found.")
                    return

                log(f"Downloading from: {final_url}. This can take a while")

                with requests.get(
                    final_url,
                    allow_redirects=True,
                    stream=True,
                    timeout=30
                ) as download:

                    download.raise_for_status()

                    total = 0

                    with open(msix_path, "wb") as file:
                        for chunk in download.iter_content(
                            chunk_size=8192
                        ):
                            if chunk:
                                file.write(chunk)
                                total += len(chunk)

                log(
                    f"Downloaded {version} "
                    f"({total / 1024 / 1024:.2f} MB)"
                )

            except Exception as e:
                log(f"Download failed: {e}")
                return

        else:
            log(f"Found existing MSIXVC: {msix_path}")

        run_logged(
            'powershell.exe -Command '
            '"Get-AppxPackage -allusers *Minecraft* '
            '| Remove-AppxPackage -allusers"',
            label="Remove Minecraft"
        )

        run_logged(
            [
                "powershell.exe",
                "-Command",
                f'Add-AppxPackage -Path "{msix_path}"'
            ],
            label="Install MSIXVC"
        )

    else:

        iPath = instance_path / "Assets"
        rmMsStoreList = ['[Content_Types].xml', 'AppxSignature.p7x', 'AppxBlockMap.xml']

        if not iPath.exists():
            log(
                f"AppXManifest.xml not found in "
                f"{instance_path}"
            )
            log("The instance needs to be created first.")
            installver = Versions.get_by_version(version)

            if not installver:
                log(f"Version {version} not found and is not available.")
                return False

            log(f"Downloading from: {installver.uri}. This can take a while")

            try:
                with requests.get(installver.uri, stream=True) as r:
                    r.raise_for_status()
                    with open(f"{instance_path}/{version}.zip", "wb") as file:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                file.write(chunk)
            except Exception as e:
                log(f"Download failed: {e}")
                raise e

            shutil.unpack_archive(f"{instance_path}/{version}.zip", extract_dir=instance_path)

            for file in rmMsStoreList:
                basePath = f"Instances/{version}/"
                if os.path.isfile(basePath+file):
                    os.remove(basePath+file)
                

        log(f"Found existing AppX instance: {instance_path}")

        
        for file in rmMsStoreList:
            basePath = f"Instances/{version}/"
            if os.path.isfile(basePath+file):
                os.remove(basePath+file)

        run_logged(
            'powershell.exe -Command '
            '"Get-AppxPackage -allusers *Minecraft* '
            '| Remove-AppxPackage -allusers"',
            label="Remove Minecraft"
        )

        run_logged(
            f'powershell.exe Add-AppxPackage -Register '
            f'"{instance_path}/AppxManifest.xml"',
            label="Register AppXManifest"
        )

    log("Launching Minecraft...")
    log("This can take a few minutes...")

    webbrowser.open("minecraft://")

    time.sleep(3)


def get_launch_logs():
    return getattr(launch, "logs", "")