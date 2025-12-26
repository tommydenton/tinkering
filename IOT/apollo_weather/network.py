#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apollo Network Status Display - Inky pHAT (250x122)
BLACK background, YELLOW (#ffff00) text and accents
Shows: SSID, IP, Ping, Last Boot
"""

import os
import subprocess
import time
from sys import exit

from PIL import Image, ImageDraw, ImageFont

from inky.auto import auto

print("APOLLO NETWORK STATUS - Initializing...")

PATH = os.path.dirname(__file__)

try:
    inky_display = auto(ask_user=True, verbose=True)
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

if inky_display.resolution not in ((212, 104), (250, 122)):
    w, h = inky_display.resolution
    raise RuntimeError("This example does not support {}x{}".format(w, h))

inky_display.set_border(inky_display.BLACK)

CITY = "Benbrook"


def get_ssid():
    """Get current WiFi SSID."""
    try:
        result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, timeout=5)
        ssid = result.stdout.strip()
        return ssid if ssid else "Not Connected"
    except:
        return "Unknown"


def get_ip():
    """Get current IP address."""
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
        ips = result.stdout.strip().split()
        return ips[0] if ips else "No IP"
    except:
        return "Unknown"


def get_ping():
    """Ping 1.1.1.1 and return latency."""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '3', '1.1.1.1'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Parse ping output for time
            for line in result.stdout.split('\n'):
                if 'time=' in line:
                    # Extract time value
                    time_part = line.split('time=')[1].split()[0]
                    return f"{time_part} ms"
        return "Timeout"
    except:
        return "Error"


def get_last_boot():
    """Get last boot time."""
    try:
        result = subprocess.run(['uptime', '-s'], capture_output=True, text=True, timeout=5)
        boot_time = result.stdout.strip()
        # Format: 2024-12-26 14:30:00 -> 12/26 14:30
        if boot_time:
            parts = boot_time.split()
            date_parts = parts[0].split('-')
            time_parts = parts[1].split(':')
            return f"{date_parts[1]}/{date_parts[2]} {time_parts[0]}:{time_parts[1]}"
        return "Unknown"
    except:
        return "Unknown"


def load_font(size):
    """Try to load NASA-style font, fall back to system fonts."""
    font_paths = [
        "/usr/share/fonts/opentype/Nasalization-Rg.otf",
        "/usr/share/fonts/opentype/nasalization.otf",
        "/usr/share/fonts/truetype/nasalization.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
    
    return ImageFont.load_default()


# Get system info
ssid = get_ssid()
ip_addr = get_ip()
ping_time = get_ping()
last_boot = get_last_boot()

print(f"SSID: {ssid}")
print(f"IP: {ip_addr}")
print(f"Ping: {ping_time}")
print(f"Boot: {last_boot}")

# Load backdrop (black background)
img = Image.open(os.path.join(PATH, "resources/backdrop_apollo.png")).resize(inky_display.resolution)
img = img.convert('RGBA')

# Colors
YELLOW = (255, 255, 0)  # #ffff00

draw = ImageDraw.Draw(img)

# Load lightning bolt icon
icon_path = os.path.join(PATH, "resources/icon-bolt-apollo.png")
if os.path.exists(icon_path):
    icon_image = Image.open(icon_path).convert('RGBA')
    mask_image = Image.new("1", icon_image.size)
    for y in range(icon_image.height):
        for x in range(icon_image.width):
            if icon_image.getpixel((x, y))[3] > 0:
                mask_image.putpixel((x, y), 255)

# Load fonts
font_sm = load_font(12)
font_med = load_font(14)

# Header: MM/DD/YY - HH:MM - Location
header_str = time.strftime("%m/%d/%y - %H:%M") + f" - {CITY.upper()}"
draw.text((18, 4), header_str, YELLOW, font=font_sm)

# Lightning bolt icon (left box area)
if os.path.exists(icon_path):
    img.paste(icon_image, (11, 55), mask_image)

# Data area - 4 rows
data_x = 50

# Row 1: SSID
draw.text((data_x, 27), f"SSID: {ssid[:15]}", YELLOW, font=font_med)

# Row 2: IP Address
draw.text((data_x, 52), f"IP: {ip_addr}", YELLOW, font=font_med)

# Row 3: Ping
draw.text((data_x, 77), f"PING: {ping_time}", YELLOW, font=font_med)

# Row 4: Last Boot
draw.text((data_x, 100), f"BOOT: {last_boot}", YELLOW, font=font_med)

# Convert to palette for Inky display
BLACK_IDX = inky_display.BLACK
WHITE_IDX = inky_display.WHITE
YELLOW_IDX = inky_display.YELLOW

pal_img = Image.new("P", img.size)
palette = [0] * 768
palette[0:3] = [0, 0, 0]
palette[3:6] = [255, 255, 255]
palette[6:9] = [255, 255, 0]
pal_img.putpalette(palette)

pixels_rgba = img.load()
pixels_pal = pal_img.load()

for y in range(img.height):
    for x in range(img.width):
        r, g, b, a = pixels_rgba[x, y]
        
        if r > 150 and g > 150 and b < 100:
            pixels_pal[x, y] = YELLOW_IDX
        elif r > 200 and g > 200 and b > 200:
            pixels_pal[x, y] = WHITE_IDX
        else:
            pixels_pal[x, y] = BLACK_IDX

inky_display.set_image(pal_img)
inky_display.show()
print("Display updated - Network Status")
