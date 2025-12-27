# Raspberry Pi Environmental Sensor Station

A complete environmental monitoring station using Adafruit STEMMA QT sensors and Mini PiTFT display on Raspberry Pi (Trixie).

## Hardware Components

| Device | I2C Address | Function |
|--------|-------------|----------|
| Mini PiTFT 135x240 | SPI (not I2C) | Color display |
| DS3231 RTC | 0x68 | Precision real-time clock |
| AHT20 | 0x38 | Temperature & humidity |
| BMP280 | 0x77 | Barometric pressure & altitude |
| SCD-41 | 0x62 | CO2, temperature, humidity |
| PA1010D GPS | 0x10 | GPS position & time |

**No I2C address conflicts!** All sensors can be daisy-chained via STEMMA QT cables.

## Wiring

```
Raspberry Pi GPIO Header
         │
         ▼
   ┌─────────────┐
   │ Mini PiTFT  │ (plugs directly onto GPIO header)
   │   135x240   │
   │             │
   │  STEMMA QT ─┼──► DS3231 ──► AHT20 ──► BMP280 ──► SCD-41 ──► PA1010D
   └─────────────┘         (daisy-chain with STEMMA QT cables)
```

The Mini PiTFT has a STEMMA QT connector on the bottom - perfect for daisy-chaining all your I2C sensors.

## Software Setup (Raspberry Pi OS Trixie)

### 1. Enable Interfaces

```bash
# Enable I2C, SPI, and Serial
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_hw 0

# Reboot to apply
sudo reboot
```

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip i2c-tools libgpiod-dev python3-libgpiod \
    fonts-dejavu python3-pil python3-numpy
```

### 3. Create Virtual Environment (Required for Trixie/Bookworm+)

```bash
# Create project directory
mkdir -p ~/sensor_station
cd ~/sensor_station

# Create and activate virtual environment
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Verify you're in the venv
which python3  # Should show /home/pi/sensor_station/.venv/bin/python3
```

### 4. Install Python Libraries

```bash
# Make sure venv is active
source ~/sensor_station/.venv/bin/activate

# Core Blinka library
pip install --upgrade adafruit-blinka

# Display library - IMPORTANT: Use RGB Display, NOT standalone st7789
# The adafruit-circuitpython-st7789 library is displayio-based and conflicts with PIL
pip install adafruit-circuitpython-rgb-display

# If you previously installed the wrong library, remove it:
pip uninstall adafruit-circuitpython-st7789

# Sensor libraries
pip install adafruit-circuitpython-ds3231      # RTC
pip install adafruit-circuitpython-ahtx0       # AHT20
pip install adafruit-circuitpython-bmp280      # BMP280
pip install adafruit-circuitpython-scd4x       # SCD-41
pip install adafruit-circuitpython-gps         # PA1010D GPS
```

### Fix for Display "x_offset" Error

If you see an error about `x_offset` or `BusDisplay`, you have a library conflict:

```bash
source ~/sensor_station/.venv/bin/activate
pip uninstall adafruit-circuitpython-st7789
pip install --upgrade adafruit-circuitpython-rgb-display
```

The `adafruit-circuitpython-rgb-display` library is PIL-compatible and works on Linux.
The standalone `adafruit-circuitpython-st7789` is displayio-based and doesn't work with PIL.

### 5. Verify I2C Devices

```bash
# Should show devices at addresses: 0x10, 0x38, 0x62, 0x68, 0x77
i2cdetect -y 1
```

Expected output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: 10 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- 38 -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- 62 -- -- -- -- -- 68 -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- 77
```

## Running the Code

```bash
cd ~/sensor_station
source .venv/bin/activate
python3 sensor_display.py
```

## Button Functions (Mini PiTFT)

- **Button A (GPIO 23)**: Cycle through display pages
- **Button B (GPIO 24)**: Toggle backlight / Wake display

## Display Pages

1. **Environmental**: Temperature, Humidity, Pressure, Altitude
2. **Air Quality**: CO2 levels with color-coded status
3. **GPS**: Latitude, Longitude, Altitude, Satellites
4. **System**: RTC time, uptime, IP address

## Troubleshooting

### "No module named board"
Make sure you're in the virtual environment:
```bash
source ~/sensor_station/.venv/bin/activate
```

### I2C device not detected
- Check STEMMA QT cable connections
- Verify I2C is enabled: `ls /dev/i2c*`
- Check for loose connections

### SCD-41 returns None
The SCD-41 takes ~5 seconds for first measurement. Code handles this automatically.

### GPS not getting fix
- GPS needs clear sky view (near window or outdoors)
- First fix can take several minutes

### Display not working
- Verify SPI is enabled
- Check that display is firmly seated on GPIO header

## Auto-start on Boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/sensor-station.service
```

```ini
[Unit]
Description=Sensor Station Display
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/sensor_station
ExecStart=/home/pi/sensor_station/.venv/bin/python3 sensor_display.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sensor-station.service
sudo systemctl start sensor-station.service
```
