#!/bin/bash

# === cabinet_startup.sh ===
# Run this at boot to fetch and run the automation script

echo "[Startup] cabinet_startup.sh started"

LOGFILE="$HOME/cabinet_startup.log"
exec > >(tee -a "$LOGFILE") 2>&1

sleep 5  # Allow time for system and network to stabilize
sudo timedatectl set-timezone Europe/Oslo

# --- Ensure dependencies ---
echo "[Startup] Installing pip and git if needed"
sudo apt-get update
sudo apt-get install -y python3-pip git

# --- Define paths ---
REPO_URL="https://github.com/pippidis/cabinet_door_closer.git"
TEMP_DIR=$(mktemp -d)
SCRIPT_DEST="$HOME/automation.py"
REQUIREMENTS_FILE="$TEMP_DIR/requirements.txt"

# --- Try to get the latest code ---
echo "[Startup] Attempting to download latest code from GitHub..."
if git clone "$REPO_URL" "$TEMP_DIR"; then
    echo "[Startup] Download successful, updating script"

    # Backup old script
    if [ -f "$SCRIPT_DEST" ]; then
        cp "$SCRIPT_DEST" "$HOME/automation_old.py"
        echo "[Startup] Old script backed up to automation_old.py"
    fi

    # Replace script
    cp "$TEMP_DIR/automation.py" "$SCRIPT_DEST"

    # Install/update requirements
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "[Startup] Installing/updating Python requirements"
        pip3 install --no-input -r "$REQUIREMENTS_FILE"
    else
        echo "[Startup] No requirements.txt found in repo"
    fi
else
    echo "[Startup] WARNING: Could not download latest code. Using existing version."
fi

# --- Cleanup ---
rm -rf "$TEMP_DIR"

# --- Run automation script ---
echo "[Startup] Running $SCRIPT_DEST"
nohup python3 "$SCRIPT_DEST" > "$HOME/automation.log" 2>&1 &

echo "[Startup] cabinet_startup.sh complete."
