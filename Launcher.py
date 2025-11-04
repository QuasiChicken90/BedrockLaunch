import webview
import threading
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
import json
import os 
import ctypes
import signal
from App.LauncherApi import libraryManager
from App.LauncherApi import launchver
from App.LauncherApi import web
from App.LauncherApi import game
from App.LauncherApi import launcher
import requests
import subprocess
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

uac_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UAC")

if os.path.isdir(uac_path):
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
else:
    if os.path.exists("App/welcome.txt"):
        os.remove("App/welcome.txt")

def getSetting(setting):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Config", "settings.json")) as f:
        data = json.load(f)
        return data[setting]

def launcherApp():

    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Views"))
    @app.route('/launcher/home')
    def home():
        return render_template('home.html', themePath=getSetting("app_themeBG"))
    
    @app.route('/launcher/settings')
    def settings():
        return render_template('Settings.html', themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/library")
    def library():
        versionList = [{"id": v, "name": v} for v in libraryManager.getInstances()]
        return render_template("library.html", versionList=versionList, themePath=getSetting("app_themeBG"))
    
    @app.route("/launcherfiles/<path:filename>")
    def launcherfiles(filename):
        return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App"), filename)

    @app.route("/launcher/launch")
    def launch():
        with open("App/selected.txt", "r") as file:
            selected_value = file.read().strip()
            if selected_value == "":
                versionList = [{"id": v, "name": v} for v in libraryManager.getInstances()]
                return render_template('Base.html', themePath=getSetting("app_themeBG"), versionList=versionList)
            
        launchver.launch(selected_value)
        return render_template('Launching.html', themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/settings/theme", methods=["GET"])
    def settings_theme():
        number = request.args.get("number")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Config", "settings.json"), "r") as f:
            data = json.load(f)
        data["app_themeBG"] = f"http://localhost:21934/launcherfiles/Themes/{number}.mp4"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Config", "settings.json"), "w") as f:
            json.dump(data, f, indent=4)
        return render_template('Base.html', themePath=getSetting("app_themeBG"))

    @app.route("/launcher/set/<version_id>")
    def set_version(version_id):
        libraryManager.setInstance(version_id)
        return render_template("Base.html", themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/create")
    def create_instance():
        return render_template("Create.html", themePath=getSetting("app_themeBG"), fullBedrockVersionList=web.getFullBedrockVersionList())
    
    @app.route("/launcher/api/create/<version>")
    def apiCreate_instance(version):
        try :
            libraryManager.createInstance(version)
            return "OK"
        except Exception as e:
            return "Error: " + str(e) + "\nTroubleshoot:\nVersions too old may not download\nCheck your internet connection\nCheck if you have enough storage"
        
    @app.route("/launcher/api/servers/getlist")
    def apiGetServers():
        servers = game.getServers()
        for s in servers:
            status = game.getServerStatus(s["ip"], s["port"])
            s.update(status)
        return jsonify(servers)

            
    @app.route("/launcher/articles")
    def articles():
        return render_template("articles.html", themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/servers/")
    def servers():
        return render_template("servers.html", themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/opendatafolder")
    def opendatafolder():
        username = os.getlogin()
        path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang"
        os.system(f"explorer.exe {path}")
        return render_template("Base.html", themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/worlds")
    def worlds():
        
        return render_template("Worlds.html", themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/api/worlds/getlist")
    def apiGetWorlds():
        return jsonify(game.getWorlds())
    
    @app.route("/launcher/api/worlds/getimage/<world>")
    def apiGetWorldImage(world):
        import os, shutil
        username = os.getlogin()
        base_path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"

        world_path = None
        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                levelname_file = os.path.join(folder_path, "levelname.txt")
                if os.path.exists(levelname_file):
                    with open(levelname_file, "r") as f:
                        name = f.read().strip()
                        if name == world:
                            world_path = folder_path
                            break

        if world_path is None:
            return "World not found", 404

        icon_path = os.path.join(world_path, "world_icon.jpeg")
        if not os.path.exists(icon_path):
            return "Icon not found", 404

        return send_file(icon_path, mimetype="image/jpeg")
    
    @app.route("/launcher/api/worlds/getsize/<world>")
    def apiGetWorldSize(world):
        size_bytes = game.getWorldSize(world)
        size_mb = round(size_bytes / (1024*1024), 2)
        return jsonify({"size": f"{size_mb} MB"})

    @app.route("/launcher/welcome")
    def welcome():
        return render_template("Welcome.html", themePath=getSetting("app_themeBG"))
    
    @app.route("/launcher/update")
    def update():
        return render_template("Updating.html")
    
    @app.route("/launcher/api/update")
    def apiUpdate():
        version = requests.get(
        "https://raw.githubusercontent.com/QuasiChicken90/BedrockLaunch/refs/heads/main/latestversion.txt"
        ).text.strip()

        launcher.fetchUpdate(f"https://github.com/QuasiChicken90/BedrockLaunch/releases/download/{version}/BedrockLaunch-{version}.zip")
        return "OK"
    
    @app.route("/launcher/api/getupdateprogress")
    def apiGetUpdateProgress():
        return jsonify(launcher.getUpdateProgress())
    
    @app.route("/launcher/api/restart")
    def apiRestart():
        base_dir = os.path.dirname(os.path.abspath(__file__))

        parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))

        bat_path = os.path.join(parent_dir, "launcher_restart.bat")

        subprocess.Popen(
            ["cmd", "/c", "start", "", bat_path],
            shell=True,
            cwd=parent_dir, 
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        os.kill(os.getpid(), signal.SIGTERM)
        return "lollllllllllllllllll"
    
    @app.route("/launcher/base")
    def base():
        if not os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "welcome.txt")):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "welcome.txt"), "w") as f:
                f.write("")
                f.close()
            return render_template("Welcome.html", themePath=getSetting("app_themeBG"))
        return render_template("Base.html", themePath=getSetting("app_themeBG"))

    app.run(host="localhost", port=21934)

flaskAppThread = threading.Thread(target=launcherApp)
flaskAppThread.start()

if os.path.isdir(uac_path):
    exe_path = os.path.join("App", "neu_wv.exe")
    if os.path.isfile(exe_path):
        app_dir = os.path.abspath("App")
        exe_full_path = os.path.abspath(exe_path)
        
        subprocess.run([exe_full_path], cwd=app_dir)
else:
    if os.path.isfile("App/welcome.txt"):
        os.remove("App/welcome.txt")
    os.system("cd BedrockLaunch && neu run")
