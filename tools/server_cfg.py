import json, os, sys

def log(status, message):
    """Renders color-coded log messages to the console."""
    colors = {
        "info": "\033[0;34m[INFO]\033[0m",
        "ok": "\033[0;32m[OK]\033[0m",
        "error": "\033[0;31m[ERROR]\033[0m",
        "warn": "\033[0;33m[WARN]\033[0m"
    }
    print(f"{colors.get(status, 'info')} {message}")

path_base = os.path.expanduser("~/hytale-server-autodeploy/server")
path_json = os.path.join(path_base, "config.json")
path_txt = os.path.join(path_base, "config.txt")

if len(sys.argv) > 1:
    password = sys.argv[1]
else:
    try:
        with open(path_txt, 'r') as f:
            password = next((l.split(":", 1)[1].strip() for l in f if l.startswith("PASSWORD:")), None)
    except FileNotFoundError:
        password = None

if password:
    data = json.load(open(path_json))
    data["Password"] = password
    json.dump(data, open(path_json, 'w'), indent=2)
    log("ok", "New passsword set")