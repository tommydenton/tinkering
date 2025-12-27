#!/usr/bin/env python3
"""
Sensor Diagnostic Tool
Tests each sensor individually for troubleshooting.

Run: python3 test_sensors.py
"""

import time
import board

def test_i2c_scan():
    """Scan I2C bus for devices."""
    print("\n" + "="*50)
    print("I2C BUS SCAN")
    print("="*50)

    try:
        import busio
        i2c = busio.I2C(board.SCL, board.SDA)

        while not i2c.try_lock():
            pass

        devices = i2c.scan()
        i2c.unlock()

        expected = {
            0x10: "PA1010D GPS",
            0x38: "AHT20",
            0x62: "SCD-41",
            0x68: "DS3231 RTC",
            0x77: "BMP280",
            0x76: "BMP280 (alt addr)",
        }

        print(f"Found {len(devices)} device(s):")
        for addr in devices:
            name = expected.get(addr, "Unknown")
            print(f"  0x{addr:02x} - {name}")

        # Check for missing expected devices
        missing = []
        for addr, name in expected.items():
            if addr not in devices and addr != 0x76:  # 0x76 is alternate
                missing.append(f"{name} (0x{addr:02x})")

        if missing:
            print(f"\n⚠ Missing: {', '.join(missing)}")

        return True
    except Exception as e:
        print(f"✗ I2C scan failed: {e}")
        return False


def test_rtc():
    """Test DS3231 RTC."""
    print("\n" + "="*50)
    print("DS3231 RTC TEST")
    print("="*50)

    try:
        import adafruit_ds3231
        i2c = board.I2C()
        rtc = adafruit_ds3231.DS3231(i2c)

        dt = rtc.datetime
        print(f"✓ Date: {dt.tm_year}-{dt.tm_mon:02d}-{dt.tm_mday:02d}")
        print(f"✓ Time: {dt.tm_hour:02d}:{dt.tm_min:02d}:{dt.tm_sec:02d}")
        print(f"✓ Temperature: {rtc.temperature:.1f}°C")

        return True
    except Exception as e:
        print(f"✗ RTC failed: {e}")
        return False


def test_aht20():
    """Test AHT20 sensor."""
    print("\n" + "="*50)
    print("AHT20 TEMPERATURE/HUMIDITY TEST")
    print("="*50)

    try:
        import adafruit_ahtx0
        i2c = board.I2C()
        aht = adafruit_ahtx0.AHTx0(i2c)

        temp_c = aht.temperature
        temp_f = (temp_c * 9/5) + 32
        humidity = aht.relative_humidity

        print(f"✓ Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
        print(f"✓ Humidity: {humidity:.1f}%")

        return True
    except Exception as e:
        print(f"✗ AHT20 failed: {e}")
        return False


def test_bmp280():
    """Test BMP280 sensor."""
    print("\n" + "="*50)
    print("BMP280 PRESSURE/ALTITUDE TEST")
    print("="*50)

    try:
        import adafruit_bmp280
        i2c = board.I2C()
        bmp = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

        # Set your local sea level pressure for accurate altitude
        bmp.sea_level_pressure = 1013.25

        temp_c = bmp.temperature
        temp_f = (temp_c * 9/5) + 32
        pressure = bmp.pressure
        altitude_m = bmp.altitude
        altitude_ft = altitude_m * 3.28084

        print(f"✓ Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
        print(f"✓ Pressure: {pressure:.2f} hPa")
        print(f"✓ Altitude: {altitude_m:.1f}m / {altitude_ft:.1f}ft")
        print(f"  (Adjust sea_level_pressure for accurate altitude)")

        return True
    except Exception as e:
        print(f"✗ BMP280 failed: {e}")
        return False


def test_scd41():
    """Test SCD-41 CO2 sensor."""
    print("\n" + "="*50)
    print("SCD-41 CO2 TEST")
    print("="*50)

    try:
        import adafruit_scd4x
        i2c = board.I2C()
        scd = adafruit_scd4x.SCD4X(i2c)

        print("Serial number:", [hex(x) for x in scd.serial_number])

        print("Starting periodic measurement...")
        scd.start_periodic_measurement()

        print("Waiting for data (up to 30 seconds)...")
        for i in range(30):
            if scd.data_ready:
                break
            print(".", end="", flush=True)
            time.sleep(1)
        print()

        if scd.data_ready:
            co2 = scd.CO2
            temp_c = scd.temperature
            temp_f = (temp_c * 9/5) + 32
            humidity = scd.relative_humidity

            print(f"✓ CO2: {co2} ppm")
            print(f"✓ Temperature: {temp_c:.2f}°C / {temp_f:.2f}°F")
            print(f"✓ Humidity: {humidity:.1f}%")

            # CO2 level interpretation
            if co2 < 800:
                print("  Level: GOOD (fresh air)")
            elif co2 < 1000:
                print("  Level: MODERATE")
            elif co2 < 1500:
                print("  Level: POOR (ventilate)")
            else:
                print("  Level: HAZARDOUS (ventilate immediately)")

            scd.stop_periodic_measurement()
            return True
        else:
            print("✗ No data after 30 seconds")
            scd.stop_periodic_measurement()
            return False

    except Exception as e:
        print(f"✗ SCD-41 failed: {e}")
        return False


def test_gps():
    """Test PA1010D GPS."""
    print("\n" + "="*50)
    print("PA1010D GPS TEST")
    print("="*50)

    try:
        import adafruit_gps
        i2c = board.I2C()
        gps = adafruit_gps.GPS_GtopI2C(i2c)

        # Turn on basic GGA and RMC sentences
        gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        gps.send_command(b"PMTK220,1000")

        print("GPS initialized, waiting for data (20 seconds)...")
        print("(GPS needs clear sky view for satellite fix)")

        start = time.monotonic()
        got_fix = False

        while time.monotonic() - start < 20:
            gps.update()

            if gps.has_fix:
                got_fix = True
                break
            elif gps.satellites is not None:
                print(f"  Satellites in view: {gps.satellites}")

            print(".", end="", flush=True)
            time.sleep(1)
        print()

        if got_fix:
            print(f"✓ GPS FIX!")
            print(f"✓ Latitude: {gps.latitude:.6f}°")
            print(f"✓ Longitude: {gps.longitude:.6f}°")
            if gps.altitude_m:
                print(f"✓ Altitude: {gps.altitude_m:.1f}m")
            if gps.satellites:
                print(f"✓ Satellites: {gps.satellites}")
            if gps.fix_quality:
                print(f"✓ Fix Quality: {gps.fix_quality}")
            return True
        else:
            print("⚠ No GPS fix (normal indoors)")
            print("  GPS communication working, just no satellite lock")
            return True  # Communication worked even without fix

    except Exception as e:
        print(f"✗ GPS failed: {e}")
        return False


def test_display():
    """Test Mini PiTFT display."""
    print("\n" + "="*50)
    print("MINI PITFT DISPLAY TEST")
    print("="*50)

    try:
        import digitalio
        import adafruit_st7789
        from PIL import Image, ImageDraw, ImageFont

        spi = board.SPI()
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D27)
        backlight = digitalio.DigitalInOut(board.D22)
        backlight.direction = digitalio.Direction.OUTPUT
        backlight.value = True

        display = adafruit_st7789.ST7789(
            spi,
            rotation=270,
            width=240,
            height=135,
            x_offset=53,
            y_offset=40,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=64000000,
        )

        # Create test image
        image = Image.new("RGB", (display.width, display.height))
        draw = ImageDraw.Draw(image)

        # Draw test pattern
        draw.rectangle((0, 0, 240, 135), fill=(0, 0, 0))
        draw.rectangle((0, 0, 240, 30), fill=(255, 0, 0))      # Red
        draw.rectangle((0, 30, 240, 60), fill=(0, 255, 0))     # Green
        draw.rectangle((0, 60, 240, 90), fill=(0, 0, 255))     # Blue
        draw.rectangle((0, 90, 240, 120), fill=(255, 255, 0))  # Yellow

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()

        draw.text((70, 115), "DISPLAY OK!", font=font, fill=(255, 255, 255))

        display.image(image)

        print("✓ Display initialized")
        print("✓ Test pattern displayed")
        print("  You should see colored bars and 'DISPLAY OK!'")

        return True

    except Exception as e:
        print(f"✗ Display failed: {e}")
        return False


def test_buttons():
    """Test Mini PiTFT buttons."""
    print("\n" + "="*50)
    print("BUTTON TEST (5 seconds)")
    print("="*50)

    try:
        import digitalio

        button_a = digitalio.DigitalInOut(board.D23)
        button_a.direction = digitalio.Direction.INPUT
        button_a.pull = digitalio.Pull.UP

        button_b = digitalio.DigitalInOut(board.D24)
        button_b.direction = digitalio.Direction.INPUT
        button_b.pull = digitalio.Pull.UP

        print("Press buttons to test (5 seconds)...")
        print("Button A = GPIO23, Button B = GPIO24")

        a_pressed = False
        b_pressed = False
        start = time.monotonic()

        while time.monotonic() - start < 5:
            if not button_a.value and not a_pressed:
                print("✓ Button A pressed!")
                a_pressed = True
            if not button_b.value and not b_pressed:
                print("✓ Button B pressed!")
                b_pressed = True
            time.sleep(0.1)

        if not a_pressed:
            print("  Button A not pressed")
        if not b_pressed:
            print("  Button B not pressed")

        return True

    except Exception as e:
        print(f"✗ Button test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("SENSOR STATION DIAGNOSTIC")
    print("="*50)

    results = {}

    results['I2C Scan'] = test_i2c_scan()
    results['Display'] = test_display()
    results['Buttons'] = test_buttons()
    results['RTC'] = test_rtc()
    results['AHT20'] = test_aht20()
    results['BMP280'] = test_bmp280()
    results['SCD-41'] = test_scd41()
    results['GPS'] = test_gps()

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    passed = 0
    failed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {passed} passed, {failed} failed")


if __name__ == "__main__":
    main()
