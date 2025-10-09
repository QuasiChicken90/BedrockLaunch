import webview
import threading
from flask import Flask, render_template, send_from_directory, request, make_response
import json
import os 
import ctypes
import signal
from App.LauncherApi import libraryManager
from App.LauncherApi import launchver
from App.LauncherApi import web
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

def getSetting(setting):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Config", "settings.json")) as f:
        data = json.load(f)
        return data[setting]
    
if getSetting("win_dpi_awareness") == True:
    ctypes.windll.shcore.SetProcessDpiAwareness(getSetting("win_dpi_awareness_level"))
    LOGPIXELSX = 88
    hDC = ctypes.windll.user32.GetDC(0)
    dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hDC, LOGPIXELSX)
    ctypes.windll.user32.ReleaseDC(0, hDC)

    # Scale factor relative to 96 DPI
    scale_factor = dpi_x / 96

    base_width, base_height = 1500, 1000

def launcherApp():

    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "App", "Views"))
    @app.route('/')
    def index():
        return render_template('Home.html', themePath=getSetting("app_themeBG"))
    
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
    
    @app.route("/launcher/quit")
    def quit():
        os.kill(os.getpid(), signal.SIGTERM)

    @app.route("/launcher/launch")
    def launch():
        with open("App/selected.txt", "r") as file:
            selected_value = file.read().strip()
            if selected_value == "":
                versionList = [{"id": v, "name": v} for v in libraryManager.getInstances()]
                return render_template('Library.html', themePath=getSetting("app_themeBG"), versionList=versionList)
            
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
        return render_template('Settings.html', themePath=getSetting("app_themeBG"))

    @app.route("/launcher/set/<version_id>")
    def set_version(version_id):
        libraryManager.setInstance(version_id)
        return render_template("Home.html", themePath=getSetting("app_themeBG"))
    
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


    app.run(host="localhost", port=21934, debug=False)

flaskAppThread = threading.Thread(target=launcherApp)
flaskAppThread.start()

webview.create_window('BedrockLaunch', 'localhost:21934', frameless=getSetting("wv_frameless_window"), easy_drag=getSetting("wv_easy_drag"), confirm_close=getSetting("wv_confirm_close"), transparent=True, width=int(base_width * scale_factor), height=int(base_height * scale_factor))
webview.start()

