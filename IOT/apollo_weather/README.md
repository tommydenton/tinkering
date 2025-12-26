# Apollo Weather Display for Inky pHAT

A NASA Mission Control inspired weather display for Pimoroni Inky pHAT (Yellow/Black/White).

## Design
- **Black background** - authentic Apollo DSKY / Mission Control style
- **Yellow (#ffff00) text** - all text in yellow for that classic amber display look
- **Yellow accents** - borders, icons, status indicators
- Mission Control style layout with rocket icon and status dots

## Installation

### 1. Install dependencies
```bash
sudo pip3 install requests geocoder
```

### 2. Copy files to your Pi
Extract the zip and copy the `apollo_weather` folder to your Pi.

### 3. (Optional) Install NASA Font
For the authentic NASA "worm" logo look, install the Nasalization font:

```bash
# Download from https://www.fontget.com/font/nasalization/
# The font is an OTF file - install like this:

sudo mkdir -p /usr/share/fonts/opentype
sudo cp Nasalization-rg.otf /usr/share/fonts/opentype/
sudo fc-cache -f -v

# Verify installation
fc-list | grep -i nasal
```

The script will auto-detect and use the NASA font if installed (supports both .otf and .ttf). Otherwise, it falls back to DejaVu Sans.

### 4. Run
```bash
cd apollo_weather
python3 weather.py
```

## Customization

Edit `weather.py` to change:
- `CITY` - Your city name
- `COUNTRYCODE` - Your country code (e.g., "US", "UK")

## Layout
```
┌────────────────────────────────┐
│🚀 12/26 14:30            ●○   │
├────┬───────────────────────────┤
│    │ TEMP: 73F                │
│    ├───────────────────────────┤
│ ☀  │ RH: 68%                  │
│    ├───────────────────────────┤
│    │ WIND: 9 MPH SSW          │
│    ├───────────────────────────┤
│    │ FEELS: 72F               │
│    ├───────────────────────────┤
│    │ LOC: BENBROOK            │
└────┴───────────────────────────┘
```
All text displays in yellow (#ffff00) on black background.

## Credits
- Weather data: Open-Meteo API (https://open-meteo.com)
- Font: Nasalization by Raymond Larabie (Typodermic Fonts)
- Inspired by NASA Mission Control displays
