import threading
from flask import Flask, render_template, send_from_directory, request, jsonify, send_file, abort
import json
import os
import ctypes
import requests
import subprocess
import sys
import re
import signal

from App.LauncherApi import libraryManager
from App.LauncherApi import launchver
from App.LauncherApi import web
from App.LauncherApi import game
from App.LauncherApi import launcher
from App.LauncherApi import versions_mcbgdk
import logging
# ─────────────────────────────────────────────
# Signal / Admin / UAC Setup
# ─────────────────────────────────────────────


def signal_handler(sig, frame):
    os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGINT, signal_handler)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

uac_path = os.path.join(os.path.dirname(os.path.abspath(__name__)), "UAC")

if os.path.isdir(uac_path):
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                            " ".join(sys.argv), None, 1)
        sys.exit()
else:
    if os.path.exists("App/welcome.txt"):
        os.remove("App/welcome.txt")

# ─────────────────────────────────────────────
# Filesystem / Startup Cleanup
# ─────────────────────────────────────────────

if os.path.isdir("Library/Addons"):
    pass
else:
    os.mkdir("Library/Addons")

if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt")):
    os.remove(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt"))

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def getSetting(setting):
    with open(
            os.path.join(os.path.dirname(os.path.abspath(__name__)), "Config",
                         "settings.json")) as f:
        data = json.load(f)
        return data[setting]

# ─────────────────────────────────────────────
# Flask App
# ─────────────────────────────────────────────

def launcherApp():

    app = Flask(__name__,
                template_folder=os.path.join(
                    os.path.dirname(os.path.abspath(__name__)), "App",
                    "Views"))
    
    @app.before_request
    def suppress_polling_logs():
        if getSetting("debug_flask_minimalLogging") == True:
            if request.path == "/launcher/api/create/getdownloadstatus":
                logging.getLogger("werkzeug").setLevel(logging.ERROR)

    # ── Static / Base Routes ──────────────────

    @app.route('/launcher/home')
    def home():
        return render_template('home.html',
                               themePath=getSetting("app_themeBG"))

    @app.route('/launcher/settings')
    def settings():
        return render_template('Settings.html',
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/base")
    def base():
        if launcher.check_developer_mode() == False:
            return render_template("Setup.html",
                                    themePath=getSetting("app_themeBG"))
        if not os.path.isfile(
                os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "welcome.txt")):
            with open(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "welcome.txt"), "w") as f:
                f.write("")
                f.close()
            return render_template("Welcome.html",
                                   themePath=getSetting("app_themeBG"))
        return render_template("Base.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/welcome")
    def welcome():
        return render_template("Welcome.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/articles")
    def articles():
        return render_template("articles.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcherfiles/<path:filename>")
    def launcherfiles(filename):
        return send_from_directory(
            os.path.join(os.path.dirname(os.path.abspath(__name__)), "App"),
            filename)

    # ── Settings Routes ───────────────────────

    @app.route("/launcher/settings/theme", methods=["GET"])
    def settings_theme():
        number = request.args.get("number")
        with open(
                os.path.join(os.path.dirname(os.path.abspath(__name__)),
                             "Config", "settings.json"), "r") as f:
            data = json.load(f)
        data[
            "app_themeBG"] = f"http://localhost:21934/launcherfiles/Themes/{number}.mp4"
        with open(
                os.path.join(os.path.dirname(os.path.abspath(__name__)),
                             "Config", "settings.json"), "w") as f:
            json.dump(data, f, indent=4)
        return render_template('Base.html',
                               themePath=getSetting("app_themeBG"))

    # ── Library Routes ────────────────────────

    @app.route("/launcher/library")
    def library():
        versionList = [{
            "id": v,
            "name": v
        } for v in libraryManager.getInstances()]
        return render_template("library.html",
                               versionList=versionList,
                               themePath=getSetting("app_themeBG"),fullBedrockVersionList=web.getFullBedrockVersionList())

    @app.route("/launcher/set/<version_id>")
    def set_version(version_id):
        libraryManager.setInstance(version_id)
        return render_template("Base.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/create")
    def create_instance():
        return render_template(
            "Create.html",
            themePath=getSetting("app_themeBG"),
            fullBedrockVersionList=web.getFullBedrockVersionList())

    @app.route("/launcher/api/create/<version>")
    def apiCreate_instance(version):
        with open(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt"), "w") as f:
            f.write("")
        try:
            match = re.search(r"(\d+\.\d+\.\d+)", version)
            if not match:
                print("Invalid version format.")
                return
            numeric_version = match.group(1)

            def parse_version(ver_str):
                parts = ver_str.split(".")
                return tuple(int(p) for p in parts)

            version_tuple = parse_version(numeric_version)
            threshold = parse_version("1.21.120")
            if version_tuple >= threshold:
                print(version)
                versions_mcbgdk.createMCBGDKInstance(version)
            else:
                libraryManager.createInstance(version)
                os.remove(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt"))
            return "OK"
        except Exception as e:
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt"))
            return "Error: " + str(
                e
            ) + "\nTroubleshoot:\nVersions too old may not download\nCheck your internet connection\nCheck if you have enough storage"

    @app.route("/launcher/api/create/getdownloadstatus")
    def apiGetDownloadStatus():
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__name__)), "App", "task_download.txt")):
            return "Downloading"
        else:
            return "NoDownload"

    # ── Launch Routes ─────────────────────────

    @app.route("/launcher/launch")
    def launch():
        with open("App/selected.txt", "r") as file:
            selected_value = file.read().strip()

            if selected_value == "":
                versionList = [{
                    "id": v,
                    "name": v
                } for v in libraryManager.getInstances()]
                
                return render_template('Base.html',
                                    themePath=getSetting("app_themeBG"),
                                    versionList=versionList)

        threading.Thread(target=launchver.launch, args=(selected_value,)).start()

        return render_template('Launching.html',
                            themePath=getSetting("app_themeBG"))

    @app.route("/launcher/launch/logs")
    def launch_logs():
        return launchver.get_launch_logs()

    # ── Game Data Routes ──────────────────────

    @app.route("/launcher/worlds")
    def worlds():
        return render_template("Worlds.html",
                            themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/worlds/getlist")
    def apiGetWorlds():
        return jsonify(game.getWorlds())

    @app.route("/launcher/api/worlds/getimage/<world>")
    def apiGetWorldImage(world):
        world_locations = game.get_world_paths()
        world_path = None
        
        for base_path in world_locations:
            if not os.path.exists(base_path):
                continue
                
            for folder in os.listdir(base_path):
                folder_path = os.path.join(base_path, folder)
                if os.path.isdir(folder_path):
                    levelname_file = os.path.join(folder_path, "levelname.txt")
                    if os.path.exists(levelname_file):
                        with open(levelname_file, "r", encoding="utf-8") as f:
                            name = f.read().strip()
                            if name == world:
                                world_path = folder_path
                                break
            
            if world_path:
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
        size_mb = round(size_bytes / (1024 * 1024), 2)
        return jsonify({"size": f"{size_mb} MB"})

    @app.route("/launcher/servers/")
    def servers():
        return render_template("servers.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/servers/getlist")
    def apiGetServers():
        servers = game.getServers()
        for s in servers:
            status = game.getServerStatus(s["ip"], s["port"])
            s.update(status)
        return jsonify(servers)

    @app.route("/launcher/screenshots")
    def screenshots():
        return render_template("Screenshots.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/screenshots/getlist")
    def apiGetScreenshots():
        return jsonify(game.getScreenshots())

    @app.route("/launcher/api/screenshots/getimage/<path:screenshot>")
    def apiGetScreenshotImage(screenshot):
        base_path = os.path.expandvars(
            r"C:\Users\%USERNAME%\AppData\Roaming\Minecraft Bedrock\Users"
        )

        requested_path = os.path.abspath(
            os.path.join(base_path, screenshot)
        )

        base_path = os.path.abspath(base_path)

        if not requested_path.startswith(base_path):
            abort(403)

        if not os.path.isfile(requested_path):
            abort(404)

        return send_file(requested_path, mimetype="image/png")

    # ── Addons / Explore Routes ───────────────

    @app.route("/launcher/explore")
    def addons():
        return render_template("Explore.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/addons/installaddon/<addon_id>")
    def install_addon(addon_id):
        game.installAddon(addon_id)
        return "OK"

    # ── File System / Folder Routes ───────────

    @app.route("/launcher/api/opendatafolder")
    def opendatafolder():
        username = os.getlogin()
        path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang"
        os.system(f"explorer.exe {path}")
        return render_template("Base.html",
                               themePath=getSetting("app_themeBG"))

    @app.route("/launcher/api/opendatafolder/mcbgdk")
    def opendatafolder_mcbgdk():
        username = os.getlogin()
        path = rf"C:\Users\pc\AppData\Roaming\Minecraft Bedrock\Users"
        os.system(f"explorer.exe {path}")
        return render_template("Base.html",
                               themePath=getSetting("app_themeBG"))

    # ── Update Routes ─────────────────────────

    @app.route("/launcher/update")
    def update():
        return render_template("Updating.html")

    @app.route("/launcher/api/update")
    def apiUpdate():
        version = requests.get(
            "https://raw.githubusercontent.com/QuasiChicken90/BedrockLaunch/refs/heads/main/latestversion.txt"
        ).text.strip()

        launcher.fetchUpdate(
            f"https://github.com/QuasiChicken90/BedrockLaunch/releases/download/{version}/BedrockLaunch-{version}.zip"
        )
        return "OK"

    @app.route("/launcher/api/getupdateprogress")
    def apiGetUpdateProgress():
        return jsonify(launcher.getUpdateProgress())

    @app.route("/launcher/api/restart")
    def apiRestart():
        base_dir = os.path.dirname(os.path.abspath(__file__))

        parent_dir = os.path.abspath(os.path.join(base_dir, os.pardir))

        bat_path = os.path.join("launcher_restart.bat")

        subprocess.Popen(["cmd", "/c", "start", "", bat_path],
                         shell=True,
                         cwd=parent_dir,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        return "lollllllllllllllllll"

    # ── Developer Routes ──────────────────────

    @app.route("/launcher/api/enabledev", methods=["POST"])
    def apiEnableDev():
        launcher.enable_developer_mode()
        return "Ok"

    app.run(host="localhost", port=21934, threaded=True)

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

flaskAppThread = threading.Thread(target=launcherApp)
flaskAppThread.start()

if os.path.isdir(uac_path):
    pass
else:
    if os.path.isfile("App/welcome.txt"):
        os.remove("App/welcome.txt")

import webview
webview.create_window("BedrockLaunch ", url="http://localhost:21934/launcher/base", min_size=(getSetting("app_minsize_w"), getSetting("app_minsize_h")), frameless=getSetting("app_frameless"), easy_drag=getSetting("app_easyDrag"))
webview.start()

os._exit(0)
