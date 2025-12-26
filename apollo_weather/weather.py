#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apollo Weather Display - Inky pHAT (250x122)
"""

import glob
import json
import os
import time
from sys import exit

from PIL import Image, ImageDraw, ImageFont

from inky.auto import auto

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")
try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

print("APOLLO WEATHER SYSTEM - Initializing...")

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
COUNTRYCODE = "US"


def degrees_to_compass(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]


def get_coords(address):
    g = geocoder.arcgis(address)
    return g.latlng


def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={coords[0]}&longitude={coords[1]}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,"
        "wind_speed_10m,apparent_temperature,wind_direction_10m"
    )
    if res.status_code == 200:
        j = json.loads(res.text)
        current = j["current"]
        weather["temperature"] = current["temperature_2m"]
        weather["windspeed"] = current["wind_speed_10m"]
        weather["humidity"] = current["relative_humidity_2m"]
        weather["weathercode"] = current["weather_code"]
        weather["feels_like"] = current["apparent_temperature"]
        weather["wind_direction"] = current["wind_direction_10m"]
    return weather


# Icon and mask storage
icons = {}
masks = {}

# Get weather
location_string = f"{CITY}, {COUNTRYCODE}"
weather = get_weather(location_string)

icon_map = {
    "snow": [71, 73, 75, 77, 85, 86],
    "rain": [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82],
    "cloud": [1, 2, 3, 45, 48],
    "sun": [0],
    "storm": [95, 96, 99],
    "wind": []
}

# Defaults
windspeed = 0.0
wind_direction = 0
temperature_f = 0.0
feels_like_f = 0.0
humidity = 0.0
weather_icon = None

if weather:
    temperature_f = (weather["temperature"] * 9/5) + 32
    feels_like_f = (weather["feels_like"] * 9/5) + 32
    windspeed = weather["windspeed"]
    wind_direction = weather["wind_direction"]
    humidity = weather["humidity"]
    weathercode = weather["weathercode"]
    
    for icon in icon_map:
        if weathercode in icon_map[icon]:
            weather_icon = icon
            break
else:
    print("WARNING: No weather data!")

# Load backdrop
img = Image.open(os.path.join(PATH, "resources/backdrop_apollo.png")).resize(inky_display.resolution)
img = img.convert('RGBA')

TEXT_COLOR = (255, 255, 255)
YELLOW_COLOR = (255, 255, 0)

draw = ImageDraw.Draw(img)

# Load icons
for icon_file in glob.glob(os.path.join(PATH, "resources/icon-*-apollo.png")):
    icon_name = icon_file.split("icon-")[1].replace("-apollo.png", "")
    icon_image = Image.open(icon_file).convert('RGBA')
    icons[icon_name] = icon_image
    
    mask_image = Image.new("1", icon_image.size)
    for y in range(icon_image.height):
        for x in range(icon_image.width):
            if icon_image.getpixel((x, y))[3] > 0:
                mask_image.putpixel((x, y), 255)
    masks[icon_name] = mask_image

# Fonts - small for this tiny screen!
try:
    from font_fredoka_one import FredokaOne
    font_sm = ImageFont.truetype(FredokaOne, 12)
    font_med = ImageFont.truetype(FredokaOne, 14)
except:
    font_sm = ImageFont.load_default()
    font_med = ImageFont.load_default()

# Header: date/time
date_str = time.strftime("%m/%d %H:%M")
draw.text((20, 4), date_str, YELLOW_COLOR, font=font_med)

# Weather icon (left box area)
if weather_icon and weather_icon in icons:
    img.paste(icons[weather_icon], (11, 50), masks[weather_icon])

# Data area (right of divider, x starts at ~48)
# Line 1: Temp and Humidity
draw.text((48, 24), f"{int(temperature_f)}°F", TEXT_COLOR, font=font_med)
draw.text((100, 24), f"RH:{int(humidity)}%", TEXT_COLOR, font=font_med)

# Line 2: Wind
windspeed_mph = windspeed * 0.621371
wind_compass = degrees_to_compass(wind_direction)
draw.text((48, 45), f"W:{int(windspeed_mph)}mph {wind_compass}", TEXT_COLOR, font=font_sm)

# Line 3: Feels like
draw.text((48, 65), f"Feels:{int(feels_like_f)}°F", TEXT_COLOR, font=font_sm)

# Line 4: Location (small)
draw.text((48, 85), f"{CITY.upper()}", YELLOW_COLOR, font=font_sm)

# Convert to palette for Inky
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
        if r > 200 and g > 200 and b < 100:
            pixels_pal[x, y] = 2  # Yellow
        elif r > 128 or g > 128 or b > 128:
            pixels_pal[x, y] = 1  # White
        else:
            pixels_pal[x, y] = 0  # Black

inky_display.set_image(pal_img)
inky_display.show()
print("Display updated.")
