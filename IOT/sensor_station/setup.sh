#!/bin/bash
#
# Sensor Station Setup Script
# For Raspberry Pi OS Trixie (Debian Testing)
#
# Usage: chmod +x setup.sh && ./setup.sh
#

set -e

INSTALL_DIR="$HOME/sensor_station"
VENV_DIR="$INSTALL_DIR/.venv"

echo "=============================================="
echo "Sensor Station Setup"
echo "=============================================="

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
fi

# Step 1: Enable interfaces
echo ""
echo "[1/5] Enabling I2C, SPI, and Serial..."
sudo raspi-config nonint do_i2c 0 || true
sudo raspi-config nonint do_spi 0 || true
sudo raspi-config nonint do_serial_hw 0 || true

# Step 2: Install system dependencies
echo ""
echo "[2/5] Installing system packages..."
sudo apt update
sudo apt install -y \
    python3-venv \
    python3-pip \
    python3-pil \
    python3-numpy \
    i2c-tools \
    libgpiod-dev \
    python3-libgpiod \
    fonts-dejavu

# Step 3: Create project directory and venv
echo ""
echo "[3/5] Creating virtual environment..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv --system-site-packages "$VENV_DIR"
fi

# Step 4: Install Python libraries
echo ""
echo "[4/5] Installing Python libraries..."
source "$VENV_DIR/bin/activate"

pip install --upgrade pip

# Core
pip install --upgrade adafruit-blinka

# Display
pip install adafruit-circuitpython-rgb-display
pip install adafruit-circuitpython-st7789

# Sensors
pip install adafruit-circuitpython-ds3231      # RTC
pip install adafruit-circuitpython-ahtx0       # AHT20
pip install adafruit-circuitpython-bmp280      # BMP280
pip install adafruit-circuitpython-scd4x       # SCD-41
pip install adafruit-circuitpython-gps         # PA1010D

# Step 5: Verify I2C
echo ""
echo "[5/5] Scanning I2C bus..."
echo ""
i2cdetect -y 1 || echo "I2C scan failed - you may need to reboot"

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Reboot if this is your first time enabling I2C/SPI:"
echo "     sudo reboot"
echo ""
echo "  2. After reboot, activate the virtual environment:"
echo "     cd $INSTALL_DIR"
echo "     source .venv/bin/activate"
echo ""
echo "  3. Run the diagnostic test:"
echo "     python3 test_sensors.py"
echo ""
echo "  4. Run the main display:"
echo "     python3 sensor_display.py"
echo ""
