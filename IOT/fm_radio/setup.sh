#!/bin/bash
#
# ScoutMakes FM Radio Setup Script
# For Raspberry Pi OS Trixie
#

set -e

INSTALL_DIR="$HOME/fm_radio"
VENV_DIR="$INSTALL_DIR/.venv"

echo "=============================================="
echo "ScoutMakes FM Radio Setup"
echo "=============================================="

# Step 1: Enable I2C
echo ""
echo "[1/4] Enabling I2C..."
sudo raspi-config nonint do_i2c 0 || true

# Step 2: Install system dependencies
echo ""
echo "[2/4] Installing system packages..."
sudo apt update
sudo apt install -y \
    python3-venv \
    python3-pip \
    i2c-tools

# Step 3: Create project directory and venv
echo ""
echo "[3/4] Creating virtual environment..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

# Step 4: Install Python libraries
echo ""
echo "[4/4] Installing Python libraries..."
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install --upgrade adafruit-blinka
pip install adafruit-circuitpython-busdevice

# Clone the RDA5807 library from GitHub
echo ""
echo "Downloading RDA5807 library..."
cd "$INSTALL_DIR"
if [ ! -d "rda5807m" ]; then
    git clone https://github.com/tinkeringtech/rda5807m.git
fi

# Copy library to project directory
cp rda5807m/tinkeringtech_rda5807m.py "$INSTALL_DIR/"

echo ""
echo "[5/5] Scanning I2C bus..."
i2cdetect -y 1 || echo "I2C scan failed - you may need to reboot"

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Hardware setup:"
echo "  1. Connect FM Radio board to Pi via STEMMA QT"
echo "  2. Attach antenna wire to ANT pad on FM board"
echo "  3. Plug headphones into 3.5mm jack on FM board"
echo ""
echo "To run:"
echo "  cd $INSTALL_DIR"
echo "  source .venv/bin/activate"
echo "  python3 fm_radio.py"
echo ""
