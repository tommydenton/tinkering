#!/usr/bin/env python3
"""
ScoutMakes FM Radio - Quick Test
Verifies the FM Radio board is connected and working
"""

import time
import board
import busio

def test_i2c_scan():
    """Scan I2C bus for devices"""
    print("\n" + "="*50)
    print("I2C BUS SCAN")
    print("="*50)
    
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        
        while not i2c.try_lock():
            pass
            
        devices = i2c.scan()
        i2c.unlock()
        
        print(f"Found {len(devices)} device(s):")
        
        expected = {
            0x11: "ScoutMakes FM Radio (RDA5807)",
            0x38: "AHT20",
            0x68: "DS3231 RTC",
            0x77: "BMP280",
        }
        
        fm_found = False
        for addr in devices:
            name = expected.get(addr, "Unknown")
            print(f"  0x{addr:02x} - {name}")
            if addr == 0x11:
                fm_found = True
                
        if not fm_found:
            print("\n⚠ FM Radio (0x11) not detected!")
            print("  Check STEMMA QT cable connection")
        else:
            print("\n✓ FM Radio detected at 0x11")
            
        return fm_found
        
    except Exception as e:
        print(f"❌ I2C scan failed: {e}")
        return False


def test_radio_init():
    """Test initializing the radio"""
    print("\n" + "="*50)
    print("FM RADIO INITIALIZATION TEST")
    print("="*50)
    
    try:
        from adafruit_bus_device.i2c_device import I2CDevice
        import tinkeringtech_rda5807m
        
        i2c = board.I2C()
        radio_i2c = I2CDevice(i2c, 0x11)
        
        print("Initializing radio at 101.1 MHz...")
        radio = tinkeringtech_rda5807m.Radio(radio_i2c, 10110, 5)
        radio.set_band("FM")
        
        time.sleep(0.5)
        
        status = radio.get_status()
        
        print(f"✓ Frequency: {status['frequency_mhz']:.1f} MHz")
        print(f"✓ Volume: {status['volume']}/15")
        print(f"✓ RSSI: {status['rssi']} dBm")
        print(f"✓ Stereo: {status['stereo']}")
        
        print("\n✓ Radio initialized successfully!")
        print("\n🎧 Connect headphones to the 3.5mm jack on the FM board")
        print("   to hear audio output.")
        
        return True
        
    except Exception as e:
        print(f"❌ Radio initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_seek():
    """Test seeking for stations"""
    print("\n" + "="*50)
    print("STATION SEEK TEST")
    print("="*50)
    
    try:
        from adafruit_bus_device.i2c_device import I2CDevice
        import tinkeringtech_rda5807m
        
        i2c = board.I2C()
        radio_i2c = I2CDevice(i2c, 0x11)
        
        radio = tinkeringtech_rda5807m.Radio(radio_i2c, 8800, 5)  # Start at 88.0 MHz
        radio.set_band("FM")
        
        print("Starting at 88.0 MHz, seeking up for stations...")
        print("(This tests that the radio chip is working)")
        
        stations_found = []
        current_freq = 8800
        
        for i in range(5):  # Find up to 5 stations
            freq = radio.seek_up()
            if freq > current_freq and freq <= 10800:
                rssi = radio.get_rssi()
                print(f"  Found: {freq/100:.1f} MHz (RSSI: {rssi} dBm)")
                stations_found.append(freq)
                current_freq = freq
            else:
                break
            time.sleep(0.3)
            
        if stations_found:
            print(f"\n✓ Found {len(stations_found)} station(s)")
            return True
        else:
            print("\n⚠ No stations found - check antenna!")
            return False
            
    except Exception as e:
        print(f"❌ Seek test failed: {e}")
        return False


def main():
    print("\n" + "="*50)
    print("SCOUTMAKES FM RADIO - DIAGNOSTIC TEST")
    print("="*50)
    
    results = {}
    
    results['I2C Scan'] = test_i2c_scan()
    
    if results['I2C Scan']:
        results['Radio Init'] = test_radio_init()
        
        if results['Radio Init']:
            results['Station Seek'] = test_seek()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test}: {status}")
        
    print()
    
    if all(results.values()):
        print("🎉 All tests passed! Your FM Radio is ready to use.")
        print("\nRun 'python3 fm_radio.py' to start the interactive radio.")
    else:
        print("❌ Some tests failed. Check connections and try again.")


if __name__ == "__main__":
    main()
