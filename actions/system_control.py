import os
import webbrowser
import subprocess

def open_website(url):
    webbrowser.open(url)

def open_application(app_name):
    apps = {
        "brave": r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Brave",
        "vs code": "code",
        "notepad": "notepad.exe"
    }

    if app_name in apps:
        subprocess.Popen(apps[app_name])
    else:
        print("Application not configured.")

def shutdown_system():
    os.system("shutdown /s /t 5")