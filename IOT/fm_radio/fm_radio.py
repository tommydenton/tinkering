#!/usr/bin/env python3
"""
ScoutMakes FM Radio - Interactive Controller
For Raspberry Pi with Blinka

Hardware:
- ScoutMakes FM Radio Board connected via STEMMA QT
- Antenna wire on ANT pad
- Headphones in 3.5mm jack on FM board

I2C Address: 0x11
"""

import time
import board
from adafruit_bus_device.i2c_device import I2CDevice
import tinkeringtech_rda5807m

# Fort Worth area FM stations (frequency in 10kHz units)
# Customize this list with your local stations!
PRESETS = [
    (8890, "KCBI 89.9"),      # Christian
    (9070, "KERA 90.7"),      # NPR
    (9710, "KLTY 97.1"),      # Christian
    (9750, "KESN 97.5"),      # ESPN Sports
    (9810, "KFWR 98.1"),      # Country
    (10030, "KTXQ 100.3"),    # Classic Rock
    (10110, "KVIL 101.1"),    # Adult Contemporary
    (10290, "KDGE 102.9"),    # Alternative
    (10650, "KLUV 106.5"),    # Oldies
]


def print_menu():
    """Print command menu"""
    print("""
╔══════════════════════════════════════════════════╗
║           ScoutMakes FM Radio                    ║
╠══════════════════════════════════════════════════╣
║  +  Volume Up          -  Volume Down            ║
║  >  Next Preset        <  Previous Preset        ║
║  u  Seek Up            d  Seek Down              ║
║  f  Set Frequency      p  Show Presets           ║
║  s  Status             m  Toggle Mute            ║
║  b  Toggle Bass Boost  r  Check RDS              ║
║  q  Quit                                         ║
╚══════════════════════════════════════════════════╝
""")


def print_presets():
    """Print preset station list"""
    print("\n📻 Preset Stations:")
    print("-" * 40)
    for i, (freq, name) in enumerate(PRESETS):
        freq_mhz = freq / 100.0
        print(f"  {i+1}. {freq_mhz:5.1f} MHz - {name}")
    print()


def print_status(radio, preset_idx):
    """Print current radio status"""
    status = radio.get_status()
    freq_mhz = status['frequency_mhz']
    
    # Find if current freq matches a preset
    preset_name = "Unknown"
    for freq, name in PRESETS:
        if abs(freq - status['frequency']) < 5:  # Within 50kHz
            preset_name = name
            break
    
    stereo = "Stereo" if status['stereo'] else "Mono"
    mute = "🔇 MUTED" if status['mute'] else ""
    bass = "🔊 Bass+" if status['bass_boost'] else ""
    
    print(f"""
┌────────────────────────────────────────┐
│  📻 {freq_mhz:5.1f} MHz - {preset_name:20s}│
│  Volume: {'█' * status['volume']}{'░' * (15 - status['volume'])} {status['volume']:2d}/15 │
│  Signal: {status['rssi']:3d} dBm  |  {stereo:6s}        │
│  {mute} {bass}                              │
└────────────────────────────────────────┘
""")


def main():
    print("\n" + "="*50)
    print("ScoutMakes FM Radio - Initializing...")
    print("="*50)
    
    # Initialize I2C
    try:
        i2c = board.I2C()
    except Exception as e:
        print(f"❌ Failed to initialize I2C: {e}")
        print("   Make sure I2C is enabled: sudo raspi-config nonint do_i2c 0")
        return
    
    # Check for FM Radio at address 0x11
    address = 0x11
    print(f"\nLooking for FM Radio at address 0x{address:02x}...")
    
    try:
        radio_i2c = I2CDevice(i2c, address)
        print("✓ FM Radio board found!")
    except Exception as e:
        print(f"❌ FM Radio not found at 0x{address:02x}")
        print(f"   Error: {e}")
        print("\n   Run 'i2cdetect -y 1' to check connected devices")
        return
    
    # Initialize RDS parser
    rds = tinkeringtech_rda5807m.RDSParser()
    
    def rds_callback(text):
        if text.strip():
            print(f"📻 RDS: {text}")
    
    rds.attach_text_callback(rds_callback)
    
    # Initialize radio
    preset_idx = 0
    initial_freq, initial_name = PRESETS[preset_idx]
    initial_volume = 5
    
    print(f"\nInitializing radio at {initial_freq/100:.1f} MHz ({initial_name})...")
    
    try:
        radio = tinkeringtech_rda5807m.Radio(radio_i2c, initial_freq, initial_volume)
        radio.attach_rds_parser(rds)
        radio.set_band("FM")
        print("✓ Radio initialized!")
    except Exception as e:
        print(f"❌ Failed to initialize radio: {e}")
        return
    
    # Wait a moment for tuning
    time.sleep(0.5)
    
    # Show initial status
    print_status(radio, preset_idx)
    print_menu()
    print("-> ", end="", flush=True)
    
    # Main loop
    try:
        while True:
            # Check for RDS data periodically
            radio.check_rds()
            
            # Check for user input (non-blocking would be better but keeping it simple)
            try:
                cmd = input().strip().lower()
            except EOFError:
                break
                
            if not cmd:
                print("-> ", end="", flush=True)
                continue
                
            if cmd == 'q':
                print("\n👋 Goodbye!")
                break
                
            elif cmd == '+':
                vol = radio.volume_up()
                print(f"🔊 Volume: {vol}/15")
                
            elif cmd == '-':
                vol = radio.volume_down()
                print(f"🔉 Volume: {vol}/15")
                
            elif cmd == '>':
                preset_idx = (preset_idx + 1) % len(PRESETS)
                freq, name = PRESETS[preset_idx]
                radio.set_frequency(freq)
                print(f"📻 Tuned to {freq/100:.1f} MHz - {name}")
                
            elif cmd == '<':
                preset_idx = (preset_idx - 1) % len(PRESETS)
                freq, name = PRESETS[preset_idx]
                radio.set_frequency(freq)
                print(f"📻 Tuned to {freq/100:.1f} MHz - {name}")
                
            elif cmd == 'u':
                print("🔍 Seeking up...")
                freq = radio.seek_up()
                print(f"📻 Found station at {freq/100:.1f} MHz")
                
            elif cmd == 'd':
                print("🔍 Seeking down...")
                freq = radio.seek_down()
                print(f"📻 Found station at {freq/100:.1f} MHz")
                
            elif cmd == 'f':
                print("Enter frequency in MHz (e.g., 101.1): ", end="", flush=True)
                try:
                    freq_input = input().strip()
                    freq_mhz = float(freq_input)
                    freq = int(freq_mhz * 100)
                    if 8700 <= freq <= 10800:
                        radio.set_frequency(freq)
                        print(f"📻 Tuned to {freq_mhz:.1f} MHz")
                    else:
                        print("❌ Frequency must be between 87.0 and 108.0 MHz")
                except ValueError:
                    print("❌ Invalid frequency")
                    
            elif cmd == 'p':
                print_presets()
                
            elif cmd == 's':
                print_status(radio, preset_idx)
                
            elif cmd == 'm':
                radio._mute = not radio._mute
                radio.set_mute(radio._mute)
                print(f"{'🔇 Muted' if radio._mute else '🔊 Unmuted'}")
                
            elif cmd == 'b':
                radio._bass_boost = not radio._bass_boost
                radio.set_bass_boost(radio._bass_boost)
                print(f"{'🔊 Bass Boost ON' if radio._bass_boost else '🔈 Bass Boost OFF'}")
                
            elif cmd == 'r':
                print("Checking RDS data...")
                for _ in range(10):
                    if radio.check_rds():
                        if rds.station_name:
                            print(f"   Station: {rds.station_name}")
                        if rds.radio_text:
                            print(f"   Text: {rds.radio_text}")
                    time.sleep(0.1)
                    
            elif cmd == '?':
                print_menu()
                
            else:
                # Check if it's a preset number
                try:
                    num = int(cmd)
                    if 1 <= num <= len(PRESETS):
                        preset_idx = num - 1
                        freq, name = PRESETS[preset_idx]
                        radio.set_frequency(freq)
                        print(f"📻 Tuned to {freq/100:.1f} MHz - {name}")
                    else:
                        print(f"❌ Unknown command: {cmd} (? for help)")
                except ValueError:
                    print(f"❌ Unknown command: {cmd} (? for help)")
                    
            print("-> ", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
