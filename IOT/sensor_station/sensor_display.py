#!/usr/bin/env python3
"""
Environmental Sensor Station
Reads multiple Adafruit STEMMA QT sensors and displays on Mini PiTFT

Sensors:
- DS3231 RTC (0x68)
- AHT20 Temperature & Humidity (0x38)
- BMP280 Barometric Pressure (0x77)
- SCD-41 CO2 Sensor (0x62)
- PA1010D GPS (0x10)

Display: Adafruit Mini PiTFT 135x240 (ST7789)

Uses adafruit_rgb_display (PIL-based) NOT adafruit_st7789 (displayio-based)
"""

import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont

# Display - use RGB Display library (PIL-compatible)
from adafruit_rgb_display import st7789

# Sensors
import adafruit_ds3231
import adafruit_ahtx0
import adafruit_bmp280
import adafruit_scd4x
import adafruit_gps


class SensorStation:
    """Environmental sensor station with display."""

    # Display colors (RGB)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    RED = (255, 0, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 128, 255)
    GRAY = (128, 128, 128)

    def __init__(self):
        """Initialize display and sensors."""
        # Initialize I2C bus
        self.i2c = board.I2C()

        # Initialize display
        self._init_display()

        # Initialize buttons
        self._init_buttons()

        # Initialize sensors
        self._init_sensors()

        # Display state
        self.current_page = 0
        self.num_pages = 4
        self.backlight_on = True
        self.last_button_time = 0
        self.last_page_change = time.monotonic()
        self.page_interval = 15.0  # Auto-rotate every 15 seconds
        
        # Network info overlay
        self.show_network = False
        self.network_info = {
            'ssid': None,
            'ip': None,
            'ping_ms': None,
        }

        # Sensor data cache
        self.sensor_data = {
            'temperature_aht': None,
            'humidity_aht': None,
            'temperature_bmp': None,
            'pressure': None,
            'altitude': None,
            'co2': None,
            'temperature_scd': None,
            'humidity_scd': None,
            'datetime': None,
            'gps_fix': False,
            'latitude': None,
            'longitude': None,
            'gps_altitude': None,
            'satellites': None,
        }

    def _init_display(self):
        """Initialize the Mini PiTFT display using RGB Display library."""
        # Configuration for CS and DC pins (PiTFT defaults)
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D27)

        # Backlight control
        self.backlight = digitalio.DigitalInOut(board.D22)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # Setup SPI bus
        spi = board.SPI()

        # Baudrate - can go up to 64MHz for faster updates
        BAUDRATE = 64000000

        # Create the ST7789 display using adafruit_rgb_display
        # For 135x240 Mini PiTFT in landscape (rotation=270)
        self.display = st7789.ST7789(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=BAUDRATE,
            width=135,
            height=240,
            x_offset=53,
            y_offset=40,
            rotation=270,  # Landscape orientation
        )

        # Create image buffer - swap dimensions for rotation
        # In rotation=270, width becomes height and vice versa
        if self.display.rotation % 180 == 90:
            self.width = self.display.height
            self.height = self.display.width
        else:
            self.width = self.display.width
            self.height = self.display.height

        self.image = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load fonts
        try:
            self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except OSError:
            # Fallback to default font
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def _init_buttons(self):
        """Initialize Mini PiTFT buttons."""
        # Button A - GPIO 23
        self.button_a = digitalio.DigitalInOut(board.D23)
        self.button_a.direction = digitalio.Direction.INPUT
        self.button_a.pull = digitalio.Pull.UP

        # Button B - GPIO 24
        self.button_b = digitalio.DigitalInOut(board.D24)
        self.button_b.direction = digitalio.Direction.INPUT
        self.button_b.pull = digitalio.Pull.UP

    def _init_sensors(self):
        """Initialize all sensors."""
        # DS3231 RTC
        try:
            self.rtc = adafruit_ds3231.DS3231(self.i2c)
            print("✓ DS3231 RTC initialized")
        except Exception as e:
            print(f"✗ DS3231 RTC failed: {e}")
            self.rtc = None

        # AHT20 Temperature & Humidity
        try:
            self.aht = adafruit_ahtx0.AHTx0(self.i2c)
            print("✓ AHT20 initialized")
        except Exception as e:
            print(f"✗ AHT20 failed: {e}")
            self.aht = None

        # BMP280 Pressure & Altitude
        try:
            self.bmp = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c)
            # Set sea level pressure for altitude calculation
            # Fort Worth area is typically around 1015-1020 hPa
            self.bmp.sea_level_pressure = 1013.25  # Adjust for your location
            print("✓ BMP280 initialized")
        except Exception as e:
            print(f"✗ BMP280 failed: {e}")
            self.bmp = None

        # SCD-41 CO2 Sensor
        try:
            self.scd = adafruit_scd4x.SCD4X(self.i2c)
            self.scd.start_periodic_measurement()
            print("✓ SCD-41 initialized (waiting for first measurement...)")
        except Exception as e:
            print(f"✗ SCD-41 failed: {e}")
            self.scd = None

        # PA1010D GPS
        try:
            self.gps = adafruit_gps.GPS_GtopI2C(self.i2c)
            # Turn on basic GGA and RMC sentences
            self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
            # Set update rate to 1Hz
            self.gps.send_command(b"PMTK220,1000")
            print("✓ PA1010D GPS initialized")
        except Exception as e:
            print(f"✗ PA1010D GPS failed: {e}")
            self.gps = None

    def read_sensors(self):
        """Read all sensor values."""
        # RTC
        if self.rtc:
            try:
                self.sensor_data['datetime'] = self.rtc.datetime
            except Exception:
                pass

        # AHT20
        if self.aht:
            try:
                self.sensor_data['temperature_aht'] = self.aht.temperature
                self.sensor_data['humidity_aht'] = self.aht.relative_humidity
            except Exception:
                pass

        # BMP280
        if self.bmp:
            try:
                self.sensor_data['temperature_bmp'] = self.bmp.temperature
                self.sensor_data['pressure'] = self.bmp.pressure
                self.sensor_data['altitude'] = self.bmp.altitude
            except Exception:
                pass

        # SCD-41 (CO2) - check if data is ready
        if self.scd:
            try:
                if self.scd.data_ready:
                    self.sensor_data['co2'] = self.scd.CO2
                    self.sensor_data['temperature_scd'] = self.scd.temperature
                    self.sensor_data['humidity_scd'] = self.scd.relative_humidity
            except Exception:
                pass

        # GPS
        if self.gps:
            try:
                self.gps.update()
                if self.gps.has_fix:
                    self.sensor_data['gps_fix'] = True
                    self.sensor_data['latitude'] = self.gps.latitude
                    self.sensor_data['longitude'] = self.gps.longitude
                    self.sensor_data['gps_altitude'] = self.gps.altitude_m
                    self.sensor_data['satellites'] = self.gps.satellites
                else:
                    self.sensor_data['gps_fix'] = False
            except Exception:
                pass

    def check_buttons(self):
        """Check button states and handle actions."""
        current_time = time.monotonic()

        # Debounce - 300ms
        if current_time - self.last_button_time < 0.3:
            return

        # Button A - toggle backlight
        if not self.button_a.value:
            self.backlight_on = not self.backlight_on
            self.backlight.value = self.backlight_on
            self.last_button_time = current_time

        # Button B - toggle network info with ping
        if not self.button_b.value:
            if self.show_network:
                self.show_network = False
            else:
                self.show_network = True
                self.update_network_info()
            self.last_button_time = current_time

    def update_network_info(self):
        """Get network info and ping 1.1.1.1"""
        import subprocess
        
        # Get SSID
        try:
            result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, timeout=5)
            self.network_info['ssid'] = result.stdout.strip() or "Not connected"
        except Exception:
            self.network_info['ssid'] = "Unknown"
        
        # Get IP address
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
            ips = result.stdout.strip().split()
            self.network_info['ip'] = ips[0] if ips else "No IP"
        except Exception:
            self.network_info['ip'] = "Unknown"
        
        # Ping 1.1.1.1
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', '1.1.1.1'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # Parse ping time from output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        ping_time = line.split('time=')[1].split()[0]
                        self.network_info['ping_ms'] = ping_time
                        break
            else:
                self.network_info['ping_ms'] = "FAIL"
        except Exception:
            self.network_info['ping_ms'] = "ERROR"

    def draw_network_overlay(self):
        """Draw network info overlay."""
        # Semi-transparent background effect - just use solid dark
        self.draw.rectangle((10, 25, self.width - 10, self.height - 10), fill=(20, 20, 40), outline=self.CYAN)
        
        y = 35
        self.draw.text((20, y), "NETWORK INFO", font=self.font_medium, fill=self.CYAN)
        y += 25
        
        self.draw.text((20, y), f"SSID: {self.network_info['ssid']}", font=self.font_small, fill=self.WHITE)
        y += 18
        
        self.draw.text((20, y), f"IP: {self.network_info['ip']}", font=self.font_small, fill=self.WHITE)
        y += 18
        
        ping = self.network_info['ping_ms']
        if ping and ping not in ('FAIL', 'ERROR'):
            color = self.GREEN
            ping_text = f"Ping: {ping}"
        else:
            color = self.RED
            ping_text = f"Ping: {ping}"
        self.draw.text((20, y), ping_text, font=self.font_small, fill=color)
        y += 22
        
        self.draw.text((20, y), "[Press B to close]", font=self.font_small, fill=self.GRAY)

    def draw_page_environmental(self):
        """Draw environmental data page (temp, humidity, pressure)."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.BLACK)

        # Title bar
        self.draw.rectangle((0, 0, self.width, 20), fill=self.BLUE)
        self.draw.text((5, 2), "ENVIRONMENTAL", font=self.font_small, fill=self.WHITE)

        y = 28

        # Temperature (average of AHT and BMP)
        temps = []
        if self.sensor_data['temperature_aht']:
            temps.append(self.sensor_data['temperature_aht'])
        if self.sensor_data['temperature_bmp']:
            temps.append(self.sensor_data['temperature_bmp'])

        if temps:
            avg_temp_c = sum(temps) / len(temps)
            avg_temp_f = (avg_temp_c * 9/5) + 32
            self.draw.text((5, y), f"Temp: {avg_temp_c:.1f}°C / {avg_temp_f:.1f}°F", font=self.font_medium, fill=self.CYAN)
        else:
            self.draw.text((5, y), "Temp: --", font=self.font_medium, fill=self.GRAY)
        y += 22

        # Humidity
        if self.sensor_data['humidity_aht']:
            hum = self.sensor_data['humidity_aht']
            color = self.GREEN if 30 <= hum <= 60 else self.YELLOW
            self.draw.text((5, y), f"Humidity: {hum:.1f}%", font=self.font_medium, fill=color)
        else:
            self.draw.text((5, y), "Humidity: --", font=self.font_medium, fill=self.GRAY)
        y += 22

        # Pressure
        if self.sensor_data['pressure']:
            press = self.sensor_data['pressure']
            self.draw.text((5, y), f"Pressure: {press:.1f} hPa", font=self.font_medium, fill=self.WHITE)
        else:
            self.draw.text((5, y), "Pressure: --", font=self.font_medium, fill=self.GRAY)
        y += 22

        # Altitude
        if self.sensor_data['altitude']:
            alt_m = self.sensor_data['altitude']
            alt_ft = alt_m * 3.28084
            self.draw.text((5, y), f"Alt: {alt_m:.0f}m / {alt_ft:.0f}ft", font=self.font_medium, fill=self.WHITE)

        # Page indicator
        self.draw.text((self.width - 25, self.height - 15), "1/4", font=self.font_small, fill=self.GRAY)

    def draw_page_air_quality(self):
        """Draw air quality page (CO2)."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.BLACK)

        # Title bar
        self.draw.rectangle((0, 0, self.width, 20), fill=self.GREEN)
        self.draw.text((5, 2), "AIR QUALITY", font=self.font_small, fill=self.BLACK)

        if self.sensor_data['co2']:
            co2 = self.sensor_data['co2']

            # Determine CO2 level and color
            if co2 < 800:
                status = "GOOD"
                color = self.GREEN
            elif co2 < 1000:
                status = "MODERATE"
                color = self.YELLOW
            elif co2 < 1500:
                status = "POOR"
                color = self.ORANGE
            else:
                status = "HAZARDOUS"
                color = self.RED

            # Large CO2 value
            self.draw.text((40, 35), f"{co2}", font=self.font_large, fill=color)
            self.draw.text((140, 45), "ppm", font=self.font_medium, fill=self.WHITE)

            # Status
            self.draw.rectangle((5, 75, self.width - 5, 95), outline=color, width=2)
            self.draw.text((80, 77), status, font=self.font_medium, fill=color)

            # SCD temperature and humidity
            y = 105
            if self.sensor_data['temperature_scd']:
                temp_c = self.sensor_data['temperature_scd']
                self.draw.text((5, y), f"T:{temp_c:.1f}°C", font=self.font_small, fill=self.GRAY)
            if self.sensor_data['humidity_scd']:
                hum = self.sensor_data['humidity_scd']
                self.draw.text((100, y), f"H:{hum:.0f}%", font=self.font_small, fill=self.GRAY)
        else:
            self.draw.text((50, 50), "Waiting for", font=self.font_medium, fill=self.YELLOW)
            self.draw.text((50, 75), "CO2 data...", font=self.font_medium, fill=self.YELLOW)

        # Page indicator
        self.draw.text((self.width - 25, self.height - 15), "2/4", font=self.font_small, fill=self.GRAY)

    def draw_page_gps(self):
        """Draw GPS page."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.BLACK)

        # Title bar
        self.draw.rectangle((0, 0, self.width, 20), fill=self.ORANGE)
        self.draw.text((5, 2), "GPS LOCATION", font=self.font_small, fill=self.BLACK)

        y = 28

        if self.sensor_data['gps_fix']:
            # Fix indicator
            self.draw.text((180, 2), "● FIX", font=self.font_small, fill=self.GREEN)

            # Latitude
            lat = self.sensor_data['latitude']
            lat_dir = "N" if lat >= 0 else "S"
            self.draw.text((5, y), f"Lat: {abs(lat):.6f}° {lat_dir}", font=self.font_medium, fill=self.WHITE)
            y += 22

            # Longitude
            lon = self.sensor_data['longitude']
            lon_dir = "E" if lon >= 0 else "W"
            self.draw.text((5, y), f"Lon: {abs(lon):.6f}° {lon_dir}", font=self.font_medium, fill=self.WHITE)
            y += 22

            # GPS Altitude
            if self.sensor_data['gps_altitude']:
                alt = self.sensor_data['gps_altitude']
                self.draw.text((5, y), f"GPS Alt: {alt:.1f}m", font=self.font_medium, fill=self.CYAN)
            y += 22

            # Satellites
            if self.sensor_data['satellites']:
                sats = self.sensor_data['satellites']
                self.draw.text((5, y), f"Satellites: {sats}", font=self.font_medium, fill=self.GREEN)
        else:
            self.draw.text((180, 2), "● NO FIX", font=self.font_small, fill=self.RED)
            self.draw.text((40, 50), "Searching for", font=self.font_medium, fill=self.YELLOW)
            self.draw.text((40, 75), "GPS signal...", font=self.font_medium, fill=self.YELLOW)

        # Page indicator
        self.draw.text((self.width - 25, self.height - 15), "3/4", font=self.font_small, fill=self.GRAY)

    def draw_page_system(self):
        """Draw system info page."""
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.BLACK)

        # Title bar
        self.draw.rectangle((0, 0, self.width, 20), fill=self.CYAN)
        self.draw.text((5, 2), "SYSTEM INFO", font=self.font_small, fill=self.BLACK)

        y = 25

        # RTC Time
        if self.sensor_data['datetime']:
            dt = self.sensor_data['datetime']
            rtc_time = f"{dt.tm_hour:02d}:{dt.tm_min:02d}:{dt.tm_sec:02d}"
            rtc_date = f"{dt.tm_year}-{dt.tm_mon:02d}-{dt.tm_mday:02d}"
            self.draw.text((5, y), f"RTC:  {rtc_time}", font=self.font_medium, fill=self.WHITE)
        else:
            self.draw.text((5, y), "RTC:  --:--:--", font=self.font_medium, fill=self.GRAY)
        y += 20

        # RPi System Time
        import time as systime
        now = systime.localtime()
        sys_time = f"{now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}"
        self.draw.text((5, y), f"RPi:  {sys_time}", font=self.font_medium, fill=self.CYAN)
        y += 20

        # Show drift if both available
        if self.sensor_data['datetime']:
            dt = self.sensor_data['datetime']
            rtc_secs = dt.tm_hour * 3600 + dt.tm_min * 60 + dt.tm_sec
            sys_secs = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
            drift = sys_secs - rtc_secs
            if abs(drift) < 2:
                self.draw.text((5, y), f"Drift: {drift:+d}s (synced)", font=self.font_small, fill=self.GREEN)
            else:
                self.draw.text((5, y), f"Drift: {drift:+d}s", font=self.font_small, fill=self.YELLOW)
        y += 18

        # Date
        if self.sensor_data['datetime']:
            self.draw.text((5, y), f"Date: {rtc_date}", font=self.font_small, fill=self.GRAY)
        y += 18

        # Sensor status
        sensors = [
            ("RTC", self.rtc is not None),
            ("AHT", self.aht is not None),
            ("BMP", self.bmp is not None),
            ("CO2", self.scd is not None and self.sensor_data['co2'] is not None),
            ("GPS", self.gps is not None),
        ]

        self.draw.text((5, y), "Sensors: ", font=self.font_small, fill=self.GRAY)
        x = 60
        for name, ok in sensors:
            color = self.GREEN if ok else self.RED
            self.draw.text((x, y), name, font=self.font_small, fill=color)
            x += 35

        # Page indicator
        self.draw.text((self.width - 25, self.height - 15), "4/4", font=self.font_small, fill=self.GRAY)

    def update_display(self):
        """Update the display with current page."""
        if self.current_page == 0:
            self.draw_page_environmental()
        elif self.current_page == 1:
            self.draw_page_air_quality()
        elif self.current_page == 2:
            self.draw_page_gps()
        elif self.current_page == 3:
            self.draw_page_system()

        # Draw network overlay on top if active
        if self.show_network:
            self.draw_network_overlay()

        # Push to display
        self.display.image(self.image)

    def run(self):
        """Main loop."""
        print("\n" + "="*50)
        print("Sensor Station Running")
        print("Button A: Toggle display | Button B: Network info")
        print("Pages auto-rotate every 15 seconds")
        print("="*50 + "\n")

        last_sensor_read = 0
        sensor_interval = 2.0  # Read sensors every 2 seconds

        try:
            while True:
                current_time = time.monotonic()

                # Check buttons
                self.check_buttons()

                # Auto-rotate pages every 15 seconds (unless network overlay is showing)
                if not self.show_network and current_time - self.last_page_change >= self.page_interval:
                    self.current_page = (self.current_page + 1) % self.num_pages
                    self.last_page_change = current_time

                # Read sensors periodically
                if current_time - last_sensor_read >= sensor_interval:
                    self.read_sensors()
                    last_sensor_read = current_time

                # Update display
                self.update_display()

                # Small delay to prevent CPU hogging
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nShutting down...")
            # Turn off backlight
            self.backlight.value = False
            # Stop SCD-41 measurements
            if self.scd:
                self.scd.stop_periodic_measurement()


def main():
    """Entry point."""
    print("Initializing Sensor Station...")
    station = SensorStation()
    station.run()


if __name__ == "__main__":
    main()
