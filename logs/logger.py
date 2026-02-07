import json
import os
from datetime import datetime

LOG_FILE = "logs/chase_log.json"

def load_logs():
    if not os.path.exists(LOG_FILE):
        return[]
    
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return[]

def save_logs(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def log_intent(intent):
    data = load_logs()

    if "intent_usage" not in data:
        data["intent_usage"] = {}

    if intent not in data["intent_usage"]:
        data["intent_usage"][intent] = 0

        data["intent_usage"][intent] += 1
        save_logs(data)

def log_error(error_message):
    data = load_logs()

    if "errors" not in data:
        data["errors"] = []

    data["errors"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": str(error_message)

    })

    save_logs(data)

def log_command(command):
    data = load_logs()
    data["command_history"].append({
        "time": str(datetime.now()),
        "command": command
    })
    save_logs(data)