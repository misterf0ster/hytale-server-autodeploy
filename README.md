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
sudo apt update && sudo apt install -y git python3 && git clone https://github.com/misterf0ster/hytale-server-autodeploy && cd hytale-server-autodeploy && python3 install.py
```

## ⚙️ Management Commands

| Action | Command |
| :--- | :--- |
| **Attach to console** | `screen -r hytale` |
| **Stop the server** | `screen -X -S hytale quit` |
| **Start the server** | `./start.sh` |
| **Detach from console** | `Ctrl + A` then `D` |


## 🛠️ How it works
The installation process follows these strictly defined steps:
1. **Dependency Check** — Verifies and installs system packages.
2. **Network Config** — Opens firewall ports in GCP.
3. **Core Sync** — Downloads official server binary.
4. **Data Unpack** — Prepares game directory structure.
5. **Start Script** — Generates a custom start.sh with optimized JVM flags.
6. **Auth Flow** — Securely links the server to your Hytale account.




