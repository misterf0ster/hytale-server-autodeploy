#!/usr/bin/env python3
import os
import subprocess
import time
import zipfile
import shutil
import sys

# config
PORT = "5520"
JAR_NAME = "HytaleServer.jar"
ASSETS_FILE = "Assets.zip"
DOWNLOADER_URL = "https://downloader.hytale.com/hytale-downloader.zip"

def log(status, message):
    """Renders color-coded log messages to the console."""
    colors = {
        "info": "\033[0;34m[INFO]\033[0m",
        "ok": "\033[0;32m[OK]\033[0m",
        "error": "\033[0;31m[ERROR]\033[0m",
        "warn": "\033[0;33m[WARN]\033[0m"
    }
    print(f"{colors.get(status, 'info')} {message}")

def get_ram():
    # Auto-detect RAM: reserve 2GB for OS, assign remainder to the server
    # Calculates max heap size based on total available system memory
    try:
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gb = int(mem_bytes / (1024**3))
        max_ram = max(4, mem_gb - 2)
        return f"{max_ram}G"
    except:
        return "4G"

def extract_oauth_url(text):
    """Extracts OAuth URL from text"""
    # Searching for a line with "Or visit:" that contains a full URL
    # Look for "Or visit:" and extract the complete link
    for line in text.split('\n'):
        if "or visit:" in line.lower() and "user_code=" in line:
            start = line.find("https://")
            if start != -1:
                url = line[start:].strip()
                for char in [' ', '\r', '\n', '\t']:
                    if char in url:
                        url = url[:url.index(char)]
                return url
    
    # If "Or visit:" is not found, search for any line containing an OAuth URL
    for line in text.split('\n'):
        if "https://" in line and "oauth.accounts.hytale.com" in line and "user_code=" in line:
            start = line.find("https://")
            if start != -1:
                url = line[start:].strip()
                for char in [' ', '\r', '\n', '\t']:
                    if char in url:
                        url = url[:url.index(char)]
                if "user_code=" in url:
                    return url
    return None

#1. Install dependencies
def install_dependencies():
    log("info", "Installing dependencies")
    subprocess.run("sudo apt update -y", shell=True, capture_output=True)
    subprocess.run("sudo apt upgrade -y", shell=True, capture_output=True)
    subprocess.run("sudo apt install -y git openjdk-25-jdk-headless screen curl unzip", shell=True, capture_output=True)
    
    log("ok", "Dependencies installed")

# 2.Open firewall ports
def open_firewall():
    log("info", "Opening ports")
    
    log("info", f"Attempting to open UDP port {PORT}...")
    subprocess.run(
        f"gcloud compute firewall-rules create hytale-game-rule --allow=udp:{PORT} --source-ranges=0.0.0.0/0 --quiet",
        shell=True, capture_output=True, text=True
    )

    log("ok", "Port opened successfully")
    #if "insufficient authentication" in result_game.stderr or "ERROR" in result_game.stderr:
    #    log("warn", "Insufficient permissions to open ports automatically")
    #    log("info", "Please open the port manually in the GCP Console:")
    #    log("info", "1. Navigate to: https://console.cloud.google.com/networking/firewalls/list")
    #    log("info", f"2. Create a rule named 'hytale-game-rule': UDP {PORT}, source 0.0.0.0/0")
    #    log("warn", "WITHOUT THIS, THE SERVER WILL BE INACCESSIBLE!")
    #else:
    #    log("ok", "Port opened successfully")

# 3.Download Hytale Downloader
def download_downloader():
    log("info", "Fetching Hytale Downloader")
    
    os.makedirs("server", exist_ok=True)
    os.chdir("server")
    
    log("info", f"Fetching downloader")
    result = subprocess.run(f"curl -L -o hytale-downloader.zip {DOWNLOADER_URL}", shell=True, capture_output=True)
    if result.returncode != 0:
        log("error", "Failed to download downloader")
        sys.exit(1)
    
    log("info", "Extracting downloader...")
    try:
        with zipfile.ZipFile("hytale-downloader.zip", 'r') as zip_ref:
            zip_ref.extractall("temp_downloader")
    except Exception as e:
        log("error", f"Extraction error: {e}")
        sys.exit(1)
    
    downloader_found = False
    for root, dirs, files in os.walk("temp_downloader"):
        for file in files:
            if "linux" in file.lower() and ("amd64" in file.lower() or "downloader" in file.lower()):
                src = os.path.join(root, file)
                shutil.move(src, "hytale-downloader")
                downloader_found = True
                log("ok", f"Located downloader: {file}")
                break
        if downloader_found:
            break
    
    os.chmod("hytale-downloader", 0o755)
    shutil.rmtree("temp_downloader", ignore_errors=True)
    
    if not os.path.exists("hytale-downloader"):
        log("error", "Downloader not found")
        sys.exit(1)
    
    log("ok", "Downloader is ready")

#4.Download server files
def download_server_files():
    log("info", "Fetching Hytale Server files")
    log("warn", "AUTHORIZATION REQUIRED:")
    
    oauth_url_captured = False
    try:
        process = subprocess.Popen(
            "./hytale-downloader",
            shell=True,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            
            clean_line = line.strip()

            if not oauth_url_captured:
                url = extract_oauth_url(line)
                if url:
                    log("warn", f"Open the link in your browser: {url}")
                    oauth_url_captured = True
                    continue
            
            if "%" in line or " / " in line:
                print(f"\r[INFO] Progress: {clean_line}", end="", flush=True)
            elif "Successfully" in line.lower():
                log("info", f"\n {clean_line}")
        
        process.wait()
        result = process
    except Exception as e:
        log("error", f"Downloader error: {e}")
        sys.exit(1)
    
    if result.returncode != 0:
        log("warn", f"Downloader exited with code {result.returncode}")
    
    zip_files = [f for f in os.listdir('.') if f.endswith('.zip') and 'downloader' not in f.lower()]
    if not zip_files:
        log("error", "Archives not found!")
        sys.exit(1)
    
    for hytale_zip in zip_files:
        log("info", f"Extracting {hytale_zip}...")
        try:
            with zipfile.ZipFile(hytale_zip, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            server_dir = os.path.join(".", "Server")
            if os.path.exists(server_dir):
                for item in os.listdir(server_dir):
                    source = os.path.join(server_dir, item)
                    dest = os.path.join(".", item)
                    
                    if os.path.exists(dest):
                        if os.path.isdir(dest):
                            shutil.rmtree(dest)
                        else:
                            os.remove(dest)
                    
                    shutil.move(source, dest)
                
                shutil.rmtree(server_dir, ignore_errors=True)
        except Exception as e:
            log("error", f"Error processing {hytale_zip}: {e}")
            sys.exit(1)
    
# 5.Create start.sh script
def start_sh():
    log("info", "Creating start.sh script...")
    
    with open("start.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Dynamic memory allocation\n")
        f.write('RAM_GB=$(python3 -c "import os; mem_bytes = os.sysconf(\'SC_PAGE_SIZE\') * os.sysconf(\'SC_PHYS_PAGES\'); mem_gb = int(mem_bytes / (1024**3)); max_ram = max(4, mem_gb - 2); print(f\'{max_ram}G\')")\n')
        
        f.write("echo \"[INFO] Allocated memory: $RAM_GB\"\n")
        f.write("mkdir -p logs\n")
        f.write(f"screen -dmS hytale java -Xms$RAM_GB -Xmx$RAM_GB -jar {JAR_NAME} --assets {ASSETS_FILE}\n")

        f.write('echo "Server started in screen session: hytale (Memory: $RAM_GB)"\n')
        f.write('echo "To attach to console: screen -r hytale"\n')
            
    os.chmod("start.sh", 0o755)
    
# 6.Authenticate server
def server_auth():
    credentials_path = os.path.expanduser("~/.hytale/auth/credentials.json")
    
    if os.path.exists(credentials_path):
        log("info", "Credentials found, skipping authentication.")
    else:
        subprocess.run(
            f"screen -dmS hytale-auth java -Xms2G -Xmx2G -jar {JAR_NAME} --assets {ASSETS_FILE}",
            shell=True, cwd=os.getcwd()
        )
        
        # Enabling full screen logging
        subprocess.run("screen -S hytale-auth -X logfile /tmp/hytale_full.log", shell=True)
        subprocess.run("screen -S hytale-auth -X log on", shell=True)
        
        log("info", "Starting authorization server...")
        time.sleep(25)
        
        subprocess.run('screen -S hytale-auth -X stuff "/auth login device\n"', shell=True)
        
        time.sleep(15)
        
        auth_url = None
        auth_success = False
        auth_url_shown = False
        
        for attempt in range(300):
            time.sleep(1)
            
            screen_content = ""
            try:
                if os.path.exists("/tmp/hytale_full.log"):
                    with open("/tmp/hytale_full.log", "r", encoding='utf-8', errors='ignore') as f:
                        screen_content = f.read()
            except:
                pass
            
            if not auth_url_shown:
                url = extract_oauth_url(screen_content)
                if url:
                    auth_url = url
            
            if any(keyword in screen_content for keyword in [
                "Authentication successful",
                "authenticated successfully",
                "Authorization successful"
            ]):
                auth_success = True
            
            if auth_url and not auth_url_shown:
                log("warn", f"Open the link in your browser: {auth_url}")
                auth_url_shown = True
            
            if auth_success:
                log("ok", "Authentication successful!")
                break
            
            if attempt % 30 == 0 and attempt > 0 and auth_url_shown:
                remaining = 300 - attempt
                print(f"Authorization pending... ({remaining}c)")
        
        if auth_success:
            subprocess.run('screen -S hytale-auth -X stuff "/auth persistence Encrypted\n"', shell=True)
            time.sleep(3)
        
        log("info", "Shutting down auth server...")
        subprocess.run("screen -S hytale-auth -X quit", shell=True)
        time.sleep(2)

#7. Start production server
def start_production_server():
    log("info", "Starting game server...")
    
    subprocess.run(
        f"screen -dmS hytale-auth bash -c 'java -Xms2G -Xmx2G -jar {JAR_NAME} --assets {ASSETS_FILE} > /tmp/hytale_full.log 2>&1'",
        shell=True, cwd=os.getcwd()
    )
    
    time.sleep(5)
    
    result = subprocess.run("screen -ls | grep hytale", shell=True, capture_output=True, text=True)
    if "hytale" in result.stdout:
        log("ok", "Server is online and ready!")
    else:
        log("warn", "Failed to confirm startup")

#8. Setup manager.sh
import os

def manager_sh():
    log("info", "Creating manager.sh script...")
    manager_content = """#!/bin/bash
# Manager script for Hytale server

BASE_DIR="$(pwd)/server"
TOOLS_DIR="$(pwd)/tools"
CONFIG_FILE="$(pwd)/config.txt"

usage() {
    echo "Command-line manager for Hytale server"
    echo "Options:"
    echo "  --all              Apply all updates"
    echo "  --mods             Update password and mods from config.txt"
    echo "  --world            Update world config"
    echo "  --clean            Clear temp files"
    echo "  --password [val]   Set password manually"
    exit 1
}

if [ $# -eq 0 ]; then usage; fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all) DO_CLEAN=true; DO_WORLD=true; DO_MODS=true; shift ;;
        --clean) DO_CLEAN=true; shift ;;
        --world) DO_WORLD=true; shift ;;
        --mods) DO_MODS=true; shift ;;
        --password) NEW_PASS="$2"; shift 2 ;;
        *) usage ;;
    esac
done

if [ "$DO_CLEAN" = true ]; then
    echo "Cleaning temporary files..."
    rm -f "$BASE_DIR"/*.zip "$BASE_DIR"/*.bak "$BASE_DIR"/*.tmp
fi

if [ "$DO_WORLD" = true ]; then
    python3 "$TOOLS_DIR/world_cfg.py"
fi

if [ -n "$NEW_PASS" ]; then
    python3 "$TOOLS_DIR/server_cfg.py" "$NEW_PASS"
elif [ "$DO_MODS" = true ]; then
    python3 "$TOOLS_DIR/server_cfg.py"
fi

if [ "$DO_MODS" = true ]; then
    echo "Updating mods..."
    rm -rf "$BASE_DIR/mods"/*
    python3 "$TOOLS_DIR/download_mods.py"
fi
"""
    with open("manager.sh", "w", encoding="utf-8") as f:
        f.write(manager_content)
    os.chmod("manager.sh", 0o755)
    log("ok", "manager.sh created successfully")

#8. Final info
def final_info(ram_size):
    log("ok", "INSTALLATION COMPLETE!")
    
    try:
        ip_result = subprocess.run("curl -s ifconfig.me", shell=True, capture_output=True, text=True, timeout=5)
        ip = ip_result.stdout.strip() if ip_result.returncode == 0 else "localhost"
    except:
        ip = "localhost"

    print(f"\nGame Server    : {ip}:{PORT}")
    print(f"Allocated RAM    : {ram_size}")
    print(f"Server Directory : {os.path.abspath('.')}")

def main():
    log("info", "Starting Hytale server deployment...")
    
    ram_size = get_ram()
    log("ok", f"Server memory allocation: {ram_size}")
    install_dependencies()
    open_firewall()
    download_downloader()
    download_server_files()
    start_sh()
    server_auth()
    start_production_server()
    manager_sh()
    final_info(ram_size)
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Installation aborted")
        sys.exit(0)
    except Exception as e:
        log("error", f"Critical error: {e}")
        sys.exit(1)