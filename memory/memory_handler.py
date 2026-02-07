import json
import os

MEMORY_FILE = "memory/memory_store.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"profile": {}, "context": {}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def set_memory(key, value):
    data = load_memory()
    data[key] = value
    save_memory(data)

def get_memory(key):
    data = load_memory()
    return data.get(key)

def update_profile(key, value):
    data = load_memory()
    if "profile" not in data:
        data["profile"] = {}
    data["profile"][key] = value
    save_memory(data)

def get_profile():
    data = load_memory()
    return data.get("profile", {})

def update_context(key, value):
    data = load_memory()
    if "context" not in data:
        data["context"] = {}
    data["context"][key] = value
    save_memory(data)

def get_context():
    data = load_memory()
    return data.get("context", {})