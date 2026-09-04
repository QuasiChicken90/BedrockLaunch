def listCombinedVersions():
    import json
    import urllib.request

    combinedVListUrl = "http://127.0.0.1:21934/api/resources/Data/appx.min.json"
    msixcombinedVListUrl = "https://raw.githubusercontent.com/LukasPAH/minecraft-windows-gdk-version-db/refs/heads/main/historical_versions.json"

    versions = []

    with urllib.request.urlopen(combinedVListUrl) as response:
        data = json.load(response)

    for version in data:
        versions.append(version[0])

    with urllib.request.urlopen(msixcombinedVListUrl) as response:
        data = json.load(response)

    for version in data["releaseVersions"]:
        versions.append(version["version"].replace("Release ", ""))

    return versions

def listAddedVersions():
    import os
    added = []
    for dir in os.listdir("Instances/"):
        if os.path.isdir(os.path.join("Instances/", dir)):
            added.append(dir)
    return added

def addVersion(version):
    import os
    if not os.path.exists(f"Instances/{version}"):
        os.makedirs(f"Instances/{version}")
        return True

def selectVersion(version):
    import os
    import shutil

    instances_path = "Instances"

    for instance in os.listdir(instances_path):
        instance_path = os.path.join(instances_path, instance)

        if os.path.isdir(instance_path):
            selected_path = os.path.join(instance_path, "selected")

            if os.path.isdir(selected_path):
                shutil.rmtree(selected_path)
    version_path = os.path.join(instances_path, version)
    selected_path = os.path.join(version_path, "selected")

    os.makedirs(selected_path, exist_ok=True)

def getSelectedVersion():
    import os

    instances_path = "Instances"

    for instance in os.listdir(instances_path):
        instance_path = os.path.join(instances_path, instance)

        if os.path.isdir(instance_path):
            selected_path = os.path.join(instance_path, "selected")

            if os.path.isdir(selected_path):
                return instance

    return None