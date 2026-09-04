from flask import Flask, redirect, render_template, send_from_directory, request, jsonify, send_file, abort
import os
from Launcher.API.launcher import prepare
from Launcher.API.launcher import fetchUpdate
from Launcher.API.launcher import check_developer_mode
from Launcher.API.launcher import enable_developer_mode
from Launcher.API.launcher import get_storage_used
from Launcher.API.launcher import opendir
from Launcher.API.vmanager import listCombinedVersions
from Launcher.API.vmanager import listAddedVersions
from Launcher.API.vmanager import addVersion
from Launcher.API.vmanager import selectVersion
from Launcher.API.vmanager import getSelectedVersion
from Launcher.API.launch import launch
from Launcher.API.launch import get_launch_logs
import threading
import requests
import subprocess

prepare()

app = Flask(__name__, template_folder="Launcher/Render")

@app.route('/')
def index():
    if check_developer_mode() == False:
        return render_template('setup.html')
    return render_template('launcher.html')

@app.route('/launcher/play')
def play():
    return render_template('play.html')

@app.route('/launcher/instances')
def instances():
    return render_template('instances.html')

@app.route('/launcher/files')
def files():
    return render_template('files.html')

@app.route('/launcher/settings')
def settings():
    return render_template('settings.html')

@app.route("/launcher/navigate/instances")
def navigate_instances():
    return redirect("/?activetab=instances")

@app.route("/launcher/navigate/settings")
def navigate_settings():
    return redirect("/?activetab=settings")


@app.route("/api/resources/<path:filename>")
def data(filename):
    resources = os.path.join(app.root_path, "Launcher", "Resources")
    return send_from_directory(resources, filename)

@app.route("/api/vmanager/listall")
def vmanagerlistall():
    return listCombinedVersions()

@app.route("/api/vmanager/addversion", methods=["POST"])
def vmanageraddversion():
    data = request.get_json()
    version = data.get("version")
    addVersion(version)
    return jsonify({"status": "success"})

@app.route("/api/vmanager/listversion")
def vmanagerlistversion():
    return listAddedVersions()

@app.route("/api/vmanager/selectversion", methods=["POST"])
def vmanagerselectver():
    data = request.get_json()
    version = data.get("selectedversion")

    selectVersion(str(version))
    return jsonify({"status": "success"})

@app.route("/api/vmanager/getselectedversion")
def vmanagergetselectedversion():
    return jsonify({"selectedversion": getSelectedVersion()})

@app.route("/api/play")
def api_play():
    launchThread = threading.Thread(
            target=launch,
            args=(getSelectedVersion(),)
        )
    launchThread.start()
    
    return render_template("launching.html")

@app.route("/api/play/getlogs")
def api_play_getlogs():
    return get_launch_logs()

@app.route("/api/core/enabledevmode", methods=["POST"])
def api_core_enabledevelopermode():
    enable_developer_mode()
    return "Ok"


@app.route("/api/core/opendir/instances")
def api_core_opendir_instances():
    opendir("Instances")
    return "Ok"

@app.route("/api/core/opendir/mc/legacy")
def api_core_opendir_mc():
    username = os.getlogin()
    path = rf"C:\Users\{username}\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang"
    opendir(path)
    return "Ok"

@app.route("/api/core/opendir/mc/")
def api_core_opendir_mc_legacy():
    username = os.getlogin()
    path = rf"C:\Users\{username}\AppData\Roaming\Minecraft Bedrock\Users"
    opendir(path)
    return "Ok"

@app.route("/api/core/getstorageusage")
def api_core_storageusage():
    used = get_storage_used()
    return jsonify({"used": used})


@app.route("/launcher/update")
def update():
    return render_template("update.html")


@app.route("/api/core/update")
def api_core_update():
    version = requests.get(
            "https://raw.githubusercontent.com/QuasiChicken90/BedrockLaunch/refs/heads/main/latestversion.txt"
        ).text.strip()

    fetchUpdate(f"https://github.com/QuasiChicken90/BedrockLaunch/releases/download/{version}/BedrockLaunch-{version}.zip")
    subprocess.Popen(["cmd", "/c", "start", "", "launcher_restart.bat"],
                         shell=True,
                         cwd=".",
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
      
    return "Ok"

app.run(host='127.0.0.1', port=21934, debug=True, use_reloader=True, threaded=True)
