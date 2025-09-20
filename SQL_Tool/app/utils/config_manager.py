# app/utils/config_manager.py

import json
import os

CONFIG_FILE = "config.json"

def save_credentials(server, username):
    """Saves the server and username to a JSON file."""
    credentials = {
        "server": server,
        "username": username
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(credentials, f, indent=4)

def load_credentials():
    """Loads the server and username from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                credentials = json.load(f)
                return credentials.get("server", ""), credentials.get("username", "")
            except json.JSONDecodeError:
                return "", ""
    return "", ""