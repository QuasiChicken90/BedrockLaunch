def getFullBedrockVersionList():
    import json
    import requests

    url = "https://raw.githubusercontent.com/ddf8196/mc-w10-versiondb-auto-update/refs/heads/master/versions.json.min"
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.text)

    versions_pre_gdk = [item[0] for item in data]

    gdk_url = "https://raw.githubusercontent.com/LukasPAH/minecraft-windows-gdk-version-db/refs/heads/main/historical_versions.json"
    gdk_response = requests.get(gdk_url)
    gdk_response.raise_for_status()
    gdk_data = json.loads(gdk_response.text)

    preview_versions = [v["version"] for v in gdk_data.get("previewVersions", [])]
    release_versions = [v["version"] for v in gdk_data.get("releaseVersions", [])]

    all_versions = versions_pre_gdk + release_versions + preview_versions

    return all_versions
