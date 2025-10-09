def launch(version):
    import signal
    import os
    import webbrowser
    from pathlib import Path

    print("setting up...")

    if os.path.isdir("launches/" + version):
        webbrowser.open("minecraft://")
    else:
        Path("launches/" + version).mkdir(parents=True, exist_ok=True)
        os.system(f'powershell.exe -Command "Get-AppxPackage -allusers *minecraftUWP* | Remove-AppxPackage -allusers"')
        os.system(f"powershell.exe Add-AppxPackage -Register Library/Installations/{version}/AppXManifest.xml")
        webbrowser.open("minecraft://")
        os.kill(os.getpid(), signal.SIGTERM)


