import os
import requests

def getServers():
    username = os.getlogin()
    path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftpe\external_servers.txt"
    
    servers = []
    
    if not os.path.exists(path):
        print("external_servers.txt not found.")
        return servers
    
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) == 4:
                index, name, ip, port = parts
                servers.append({
                    "index": int(index),
                    "name": name,
                    "ip": ip,
                    "port": int(port)
                })
            else:
                print(f"malformed line >  {line}")
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

def getWorlds():
    username = os.getlogin()
    worldnames = []
    path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"
    for world in os.listdir(path):
        world_path = os.path.join(path, world)
        if os.path.isfile(f"{world_path}/levelname.txt"):
            with open(f"{world_path}/levelname.txt", "r") as f:
                worldnames.append(f.read())
    return worldnames

def getWorldImage(world):
    username = os.getlogin()
    path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds\{world}\world_icon.jpeg"
    return path
    
def getWorldSize(world_folder_name):
    import os
    username = os.getlogin()
    base_path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"
    total_size = 0
    world_path = None

    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            levelname_file = os.path.join(folder_path, "levelname.txt")
            if os.path.exists(levelname_file):
                with open(levelname_file, "r") as f:
                    name = f.read().strip()
                    if name == world_folder_name:
                        world_path = folder_path
                        break

    if world_path is None:
        return 0

    for dirpath, dirnames, filenames in os.walk(world_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)

    return total_size
