import json
import os


def get_cache_file():
    home = os.path.expanduser("~")

    # Windows
    if os.name == "nt":
        base = os.getenv("APPDATA")

    # macOS/Linux
    else:
        base = home

    folder = os.path.join(base, ".my_new_launcher")

    os.makedirs(folder, exist_ok=True)

    return os.path.join(folder, "accounts.json")


CACHE_FILE = get_cache_file()


def save_account(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_account():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    return None