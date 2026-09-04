def createMCBGDKInstance(version):
    import requests
    from . import web
    import os

    allvers = web.getFullBedrockVersionList()
    if version in allvers:
        print("Found version, downloading...")
    else:
        raise Exception("Version not found")

    gdkverslink = "https://raw.githubusercontent.com/LukasPAH/minecraft-windows-gdk-version-db/refs/heads/main/historical_versions.json"

    response = requests.get(gdkverslink)
    data = response.json()

    final_url = None
    for entry in data.get("previewVersions", []) + data.get("releaseVersions", []):
        if entry["version"] == version:
            final_url = entry["urls"][0] 
            break

    if not final_url:
        raise Exception(f"GDK URL for version {version} not found.")

    print("Downloading from:", final_url)

    os.makedirs(f"Library/Installations/{version}", exist_ok=True)

    response = requests.get(final_url, allow_redirects=True, stream=True)
    print("Status:", response.status_code)
    print("Final URL:", response.url)

    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}\n{response.text[:200]}")

    with open(f"Library/Installations/{version}/MinecraftBedrockGDK.msixvc", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    print(f"Downloaded {version} successfully.")
