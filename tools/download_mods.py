import os, urllib.request, sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODS_DIR = os.path.join(ROOT_DIR, "server", "mods")
CONFIG_TXT = os.path.join(ROOT_DIR, "config.txt")

def log(status, message):
    colors = {"info": "\033[0;34m[INFO]\033[0m", "ok": "\033[0;32m[OK]\033[0m", "error": "\033[0;31m[ERROR]\033[0m"}
    print(f"{colors.get(status, 'info')} {message}")

if not os.path.exists(CONFIG_TXT):
    log("error", "config.txt not found. Create it in the root folder.")
    sys.exit(1)

urls = [l.split(":", 1)[1].strip() for l in open(CONFIG_TXT) if l.startswith("MOD:")]
os.makedirs(MODS_DIR, exist_ok=True)

for i, url in enumerate(urls):
    name = f"mod_{i+1}.jar"
    log("info", f"Downloading {url} as {name}...")
    try:
        urllib.request.urlretrieve(url, os.path.join(MODS_DIR, name))
    except Exception as e:
        log("error", f"Failed: {e}")

log("ok", f"Sync complete. Total mods in folder: {len(urls)}")