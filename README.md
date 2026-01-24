# 🏰 Hytale Server Auto-Deploy

<p align="center">
  <img src="https://img.shields.io/badge/Hytale-Latest-orange?style=for-the-badge&logo=hytale" alt="Hytale Version">
  <img src="https://img.shields.io/badge/Java-25-red?style=for-the-badge&logo=openjdk" alt="Java Version">
  <img src="https://img.shields.io/badge/Platform-Google_Cloud-blue?style=for-the-badge&logo=google-cloud" alt="Platform">
</p>

### 🌟 Overview
Automated script for instant Hytale server deployment on **Google Cloud Platform**. The script handles full system configuration, optimizes RAM allocation, and manages dependencies out of the box.

## 📋 Requirements

- **OS**: Ubuntu 24.04 LTS
- **Disk**: 30+ GB Free Space
- **RAM**: 4GB Minimum (8GB+ Recommended)
- **Network**: Stable connection (10-20 GB download)

## 🚀 Quick Start (SSH)

Connect to your Google Cloud VM and run this single command to start the installation:

```bash
sudo apt update && sudo apt install -y git python3 && git clone https://github.com/misterf0ster/hytale-server-autodeploy && cd hytale-server-autodeploy && python3 gcp-installer.py
```

## ⚙️ Server Management Commands

| Action | Command |
| :--- | :--- |
| **Attach to console** | `screen -r hytale` |
| **Stop the server** | `screen -X -S hytale quit` |
| **Start the server** | `./start.sh` |
| **Detach from console** | `Ctrl + A` then `D` |


## 🛠️ Server Management Tool (CLI)
After the installation is complete, a manager.sh script is automatically generated in the root directory. This tool allows you to manage server settings and mods without manual JSON editing.

## ⚙️ Management Commands Tool

| Action | Command |
| :--- | :--- |
| **Full Sync** | `./manager.sh --all` |
| **Update Mods & Pass** | `./manager.sh --mods` |
| **Manual Password** | `./manager.sh --password <your_pass>` |
| **Reset World Config** | `./manager.sh --world` |
| **Cleanup Junk** | `./manager.sh --clean` |


## 📝 Mod & Password Configuration (config.txt)
To synchronize mods and update the server password, create a config.txt file in the root folder:
```
PASSWORD: my_secure_password
MOD: https://example.com/mod-archive-1.jar
MOD: https://example.com/mod-archive-2.jar
```