import glob
import os
import requests
import os
import yaml

def getServers():
    username = os.getlogin()
    servers = []

    primary_path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftpe\external_servers.txt"
    
    roaming_base = rf"C:\Users\{username}\AppData\Roaming\Minecraft Bedrock\Users"

    paths_to_check = []

    if os.path.exists(primary_path):
        paths_to_check.append(primary_path)
    else:
        print("primary external_servers.txt not found, scanning Roaming...")

    if os.path.exists(roaming_base):
        for root, dirs, files in os.walk(roaming_base):
            if "external_servers.txt" in files:
                paths_to_check.append(os.path.join(root, "external_servers.txt"))

    for path in paths_to_check:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(":")
                if len(parts) >= 4:
                    try:
                        index, name, ip, port = parts[:4]
                        servers.append({
                            "index": int(index),
                            "name": name,
                            "ip": ip,
                            "port": int(port)
                        })
                    except ValueError:
                        print(f"Invalid data in line > {line}")
                else:
                    print(f"malformed line > {line}")

    return servers


def getServerStatus(ip, port):
    try:
        response = requests.get(f"https://api.mcsrvstat.us/bedrock/2/{ip}:{port}", timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {
            "online": False,
            "error": str(e)
        }
    
    version = data.get("version", "Unknown")
    online = data.get("online", False)
    players = data.get("players", {}).get("online", 0)
    motd = data.get("motd", {}).get("clean", ["Unknown MOTD"])[0]
    
    return {
        "version": version,
        "online": online,
        "players_online": players,
        "motd": motd
    }

def get_world_paths():
    username = os.getlogin()

    uwp_path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"
    
    roaming_base = rf"C:\Users\{username}\AppData\Roaming\Minecraft Bedrock\Users"

    paths = []

    if os.path.exists(uwp_path):
        paths.append(uwp_path)

    if os.path.exists(roaming_base):
        for user_folder in os.listdir(roaming_base):
            user_folder_path = os.path.join(roaming_base, user_folder)
            
            if os.path.isdir(user_folder_path):
                games_path = os.path.join(user_folder_path, "games")
                if os.path.exists(games_path):
                    
                    com_mojang_path = os.path.join(games_path, "com.mojang")
                    if os.path.exists(com_mojang_path):
                        
                        worlds_path = os.path.join(com_mojang_path, "minecraftWorlds")
                        if os.path.exists(worlds_path):
                            paths.append(worlds_path)

    return paths

def getWorlds():
    worldnames = []
    world_locations = get_world_paths()
    
    for path in world_locations:
        if not os.path.exists(path):
            continue
        
        worlds = os.listdir(path)
        
        for world in worlds:
            world_path = os.path.join(path, world)
            
            if not os.path.isdir(world_path):
                continue
        
            
            levelname_file = os.path.join(world_path, "levelname.txt")
            
            if os.path.isfile(levelname_file):
                with open(levelname_file, "r", encoding="utf-8") as f:
                    name = f.read().strip()
                    worldnames.append(name)
            else:
                print(f"No levelname.txt in {world}")  
    
    return worldnames

def getWorldImage(world_folder_name):
    world_locations = get_world_paths()

    for path in world_locations:
        icon_path = os.path.join(path, world_folder_name, "world_icon.jpeg")
        if os.path.exists(icon_path):
            return icon_path

    return None

def getWorldSize(world_display_name):
    total_size = 0
    world_folder = None
    world_locations = get_world_paths()

    for base_path in world_locations:
        if not os.path.exists(base_path):
            continue

        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)
            levelname_file = os.path.join(folder_path, "levelname.txt")

            if os.path.isfile(levelname_file):
                with open(levelname_file, "r", encoding="utf-8") as f:
                    name = f.read().strip()
                    if name == world_display_name:
                        world_folder = folder_path
                        break

        if world_folder:
            break

    if not world_folder:
        return 0
    
    for dirpath, _, filenames in os.walk(world_folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)

    return total_size

def installAddon(id):
    addondb = "https://raw.githubusercontent.com/QuasiChicken90/BedrockLaunch/refs/heads/main/Addons/AddonDB.yml"
    addondb = requests.get(addondb).text
    addondb = yaml.safe_load(addondb)
    id = str(id)
    id = id.replace('"', '')
    
    if id in addondb:
        addon = addondb[id]
        api_url = addon["DownloadURL"]
        name = addon["Name"]
        author = addon["Author"]
        type = addon["Type"]
        
        print(f"Fetching release info for {name} by {author}...")
        
        try:
            release_response = requests.get(api_url)
            release_response.raise_for_status()
            release_data = release_response.json()
            
            if "assets" in release_data and len(release_data["assets"]) > 0:
                download_url = release_data["assets"][0]["browser_download_url"]
                print(f"Installing {name} from {download_url}")
                
                os.makedirs("Library/Addons/" + id, exist_ok=True)
                
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    with open("Library/Addons/" + id + f"/pack.{type}", "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                

                print(f"Successfully downloaded {name}!")

            else:
                print(f"No assets found in the latest release for {name}")
                
        except Exception as e:
            print(f"Download failed: {e}")
            raise e
    else:
        print(f"Addon {id} not found.")


import os
import glob

def getScreenshots():
    base_path = os.path.expandvars(
        r"C:\Users\%USERNAME%\AppData\Roaming\Minecraft Bedrock\Users"
    )
    
    png_files = []
    
    if os.path.exists(base_path):
        for user_folder in os.listdir(base_path):
            screenshots_path = os.path.join(
                base_path,
                user_folder,
                "games",
                "com.mojang",
                "Screenshots"
            )
            
            if os.path.exists(screenshots_path):
                png_files.extend(
                    glob.glob(os.path.join(screenshots_path, "**", "*.jpeg"), recursive=True)
                )
    
    return png_files
