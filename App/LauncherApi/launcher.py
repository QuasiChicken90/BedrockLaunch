progress = 0

def fetchUpdate(updateURL):
    global progress
    import requests

    progress = 10
    print("Downloading from:", updateURL)

    response = requests.get(updateURL, allow_redirects=True, stream=True)
    print("Status:", response.status_code)
    print("Final URL:", response.url)

    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}\n{response.text[:200]}")

    progress = 30
    with open("update.zip", "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    progress = 100


def getUpdateProgress():
    global progress
    return progress
