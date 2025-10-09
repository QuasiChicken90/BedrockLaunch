def getFullBedrockVersionList():
    import json
    import requests

    url = "https://raw.githubusercontent.com/ddf8196/mc-w10-versiondb-auto-update/refs/heads/master/versions.json.min"
    response = requests.get(url)
    data = json.loads(response.text)

    versions = [item[0] for item in data]

    return versions
