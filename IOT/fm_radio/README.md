# ScoutMakes FM Radio for Raspberry Pi

Control the ScoutMakes FM Radio Board via I2C from a Raspberry Pi running Blinka.

## Hardware

| Component | Details |
|-----------|---------|
| ScoutMakes FM Radio Board | I2C address 0x11, RDA5807 chip |
| Connection | STEMMA QT cable to Mini PiTFT or Pi's I2C pins |
| Audio Output | 3.5mm jack **on the FM board** (not the Pi) |
| Antenna | Wire soldered to ANT pad for good reception |

## Wiring

Connect via STEMMA QT from the Mini PiTFT's bottom connector:

```
Mini PiTFT STEMMA QT ──► ScoutMakes FM Radio Board
```

Or direct to Pi GPIO:
- VCC → 3.3V (Pin 1)
- GND → GND (Pin 6)
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)

**Important:** Plug headphones into the 3.5mm jack on the FM Radio board, not the Pi!

## Quick Start

```bash
# Clone/copy files to Pi
cd ~/fm_radio

# Run setup
chmod +x setup.sh
./setup.sh

# Reboot if first time enabling I2C
sudo reboot

# After reboot, activate venv and test
cd ~/fm_radio
source .venv/bin/activate
python3 test_fm_radio.py

# Run interactive radio
python3 fm_radio.py
```

## Verifying Connection

```bash
# Should show device at 0x11
i2cdetect -y 1
```

Expected output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- 11 -- -- -- -- -- -- -- -- -- -- -- -- -- --
...
```

## Interactive Commands

| Command | Action |
|---------|--------|
| `+` | Volume up |
| `-` | Volume down |
| `>` | Next preset station |
| `<` | Previous preset station |
| `u` | Seek up (find next station) |
| `d` | Seek down |
| `f` | Enter frequency manually |
| `p` | Show preset list |
| `s` | Show status |
| `m` | Toggle mute |
| `b` | Toggle bass boost |
| `r` | Check RDS data |
| `1-9` | Jump to preset number |
| `q` | Quit |

## Customizing Presets

Edit `fm_radio.py` and modify the `PRESETS` list with your local stations:

```python
PRESETS = [
    (8890, "Station Name"),   # 88.9 MHz
    (9710, "Another Station"), # 97.1 MHz
    # Add your stations here...
]
```

Frequency format: `10110` = 101.1 MHz (multiply MHz by 100)

## Antenna

For good reception, solder a wire (about 30 inches / 75cm for FM) to the ANT pad on the board. Even a short wire helps significantly.

## Troubleshooting

### No device at 0x11
- Check STEMMA QT cable is fully seated
- Verify I2C is enabled: `sudo raspi-config nonint do_i2c 0`
- Check power LED on FM board is lit

### No audio
- Headphones must be in the FM board's 3.5mm jack, not the Pi
- Check volume isn't 0 or muted
- Try seeking to find a strong station

### Weak reception / static
- Add or lengthen antenna wire
- Move away from electronic interference
- Try different station

### RDS not showing
- Not all stations broadcast RDS
- RDS data takes a few seconds to appear
- Try a major commercial station

## Files

| File | Description |
|------|-------------|
| `setup.sh` | Installation script |
| `tinkeringtech_rda5807m.py` | RDA5807 driver library |
| `fm_radio.py` | Interactive radio controller |
| `test_fm_radio.py` | Hardware diagnostic test |
