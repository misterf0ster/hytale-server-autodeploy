import json, os

def log(status, message):
    """Renders color-coded log messages to the console."""
    colors = {
        "info": "\033[0;34m[INFO]\033[0m",
        "ok": "\033[0;32m[OK]\033[0m",
        "error": "\033[0;31m[ERROR]\033[0m",
        "warn": "\033[0;33m[WARN]\033[0m"
    }
    print(f"{colors.get(status, 'info')} {message}")

path = os.path.expanduser("~/hytale-server-autodeploy/server/universe/worlds/default/config.json")
data = json.load(open(path))
data["IsPvpEnabled"] = True
data["Death"] = {
    "RespawnController": {"Type": "HomeOrSpawnPoint"},
    "ItemsLossMode": "All",
    "ItemsAmountLossPercentage": 10.0,
    "ItemsDurabilityLossPercentage": 10.0
}
json.dump(data, open(path, 'w'), indent=2)
log("ok", "World configuration updated!")