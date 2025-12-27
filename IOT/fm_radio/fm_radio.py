#!/usr/bin/env python3
"""
ScoutMakes FM Radio - Curses Interface
Fixed menu at top, scrolling log below
Works great over SSH

Controls:
  +/=  Volume Up       -    Volume Down
  >/. Next Preset     </,  Previous Preset
  u    Seek Up         d    Seek Down
  m    Toggle Mute     b    Toggle Bass
  s    Toggle Stereo   r    Check RDS
  1-9  Jump to Preset  q    Quit
"""

import curses
import time
import board
from adafruit_bus_device.i2c_device import I2CDevice
import tinkeringtech_rda5807m

# Fort Worth area FM stations (frequency in 10kHz units)
PRESETS = [
    (8890, "KCBI 89.9"),
    (9070, "KERA 90.7"),
    (9710, "KLTY 97.1"),
    (9750, "KESN 97.5"),
    (9810, "KFWR 98.1"),
    (10030, "KTXQ 100.3"),
    (10110, "KVIL 101.1"),
    (10290, "KDGE 102.9"),
    (10650, "KLUV 106.5"),
]


class FMRadioUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.log_lines = []
        self.max_log_lines = 100
        self.preset_idx = 0
        self.rds_text = ""
        self.radio = None
        self.rds = None
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # Frequency
        curses.init_pair(2, curses.COLOR_GREEN, -1)   # Good/On
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Warning
        curses.init_pair(4, curses.COLOR_RED, -1)     # Off/Error
        curses.init_pair(5, curses.COLOR_MAGENTA, -1) # RDS
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
        
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(100)   # 100ms timeout for getch
        
    def log(self, message):
        """Add message to scrolling log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_lines.append(f"{timestamp} {message}")
        if len(self.log_lines) > self.max_log_lines:
            self.log_lines.pop(0)
            
    def init_radio(self):
        """Initialize the FM radio hardware"""
        self.log("Initializing I2C...")
        try:
            i2c = board.I2C()
            radio_i2c = I2CDevice(i2c, 0x11)
            self.log("✓ FM Radio found at 0x11")
        except Exception as e:
            self.log(f"✗ FM Radio not found: {e}")
            return False
            
        self.rds = tinkeringtech_rda5807m.RDSParser()
        self.rds.attach_text_callback(self.rds_callback)
        
        freq, name = PRESETS[self.preset_idx]
        self.log(f"Tuning to {freq/100:.1f} MHz ({name})...")
        
        try:
            self.radio = tinkeringtech_rda5807m.Radio(radio_i2c, freq, 5)
            self.radio.attach_rds_parser(self.rds)
            self.radio.set_band("FM")
            self.log("✓ Radio initialized!")
            return True
        except Exception as e:
            self.log(f"✗ Radio init failed: {e}")
            return False
            
    def rds_callback(self, text):
        """Handle RDS text updates"""
        if text.strip():
            self.rds_text = text.strip()
            self.log(f"RDS: {self.rds_text}")
            
    def draw_header(self):
        """Draw fixed header with status and menu"""
        height, width = self.stdscr.getmaxyx()
        
        # Clear header area
        for i in range(12):
            self.stdscr.move(i, 0)
            self.stdscr.clrtoeol()
            
        # Title bar
        title = " ScoutMakes FM Radio "
        self.stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * width)
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
        
        if self.radio:
            status = self.radio.get_status()
            freq_mhz = status['frequency_mhz']
            
            # Find preset name
            preset_name = "Unknown"
            for freq, name in PRESETS:
                if abs(freq - status['frequency']) < 5:
                    preset_name = name
                    break
                    
            # Frequency display
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(2, 2, f"📻 {freq_mhz:5.1f} MHz")
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(2, 20, f"- {preset_name}")
            
            # Volume bar
            vol = status['volume']
            vol_bar = "█" * vol + "░" * (15 - vol)
            self.stdscr.addstr(3, 2, f"Vol: [{vol_bar}] {vol:2d}/15")
            
            # Status indicators
            col = 2
            
            # Stereo/Mono
            if status['stereo']:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(4, col, "STEREO")
                self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(4, col, "MONO  ")
                self.stdscr.attroff(curses.color_pair(3))
            col += 8
            
            # Signal strength
            rssi = status['rssi']
            if rssi > 40:
                color = curses.color_pair(2)
            elif rssi > 20:
                color = curses.color_pair(3)
            else:
                color = curses.color_pair(4)
            self.stdscr.attron(color)
            self.stdscr.addstr(4, col, f"RSSI:{rssi:3d}")
            self.stdscr.attroff(color)
            col += 10
            
            # Mute
            if status['mute']:
                self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                self.stdscr.addstr(4, col, "MUTED")
                self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            col += 7
            
            # Bass
            if status['bass_boost']:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(4, col, "BASS+")
                self.stdscr.attroff(curses.color_pair(2))
                
            # RDS text
            if self.rds_text:
                self.stdscr.attron(curses.color_pair(5))
                rds_display = self.rds_text[:width-4]
                self.stdscr.addstr(5, 2, f"RDS: {rds_display}")
                self.stdscr.attroff(curses.color_pair(5))
        else:
            self.stdscr.attron(curses.color_pair(4))
            self.stdscr.addstr(2, 2, "Radio not initialized")
            self.stdscr.attroff(curses.color_pair(4))
            
        # Menu
        self.stdscr.addstr(7, 0, "─" * width)
        menu1 = " +/- Vol   >/< Preset   u/d Seek   f Freq   1-9 Presets "
        menu2 = " m Mute    b Bass       s Stereo   r RDS    p List   q Quit "
        self.stdscr.addstr(8, 2, menu1)
        self.stdscr.addstr(9, 2, menu2)
        self.stdscr.addstr(10, 0, "─" * width)
        
    def draw_log(self):
        """Draw scrolling log area"""
        height, width = self.stdscr.getmaxyx()
        log_start = 11
        log_height = height - log_start - 1
        
        # Show last N lines that fit
        visible_lines = self.log_lines[-log_height:]
        
        for i, line in enumerate(visible_lines):
            y = log_start + i
            if y < height - 1:
                self.stdscr.move(y, 0)
                self.stdscr.clrtoeol()
                # Truncate line if too long
                display_line = line[:width-1]
                self.stdscr.addstr(y, 0, display_line)
                
    def draw(self):
        """Draw entire screen"""
        try:
            self.draw_header()
            self.draw_log()
            self.stdscr.refresh()
        except curses.error:
            pass  # Handle terminal resize gracefully
            
    def handle_input(self, key):
        """Handle keyboard input"""
        if key == -1:
            return True
            
        ch = chr(key) if 0 <= key < 256 else ''
        
        if ch in 'qQ':
            return False
            
        if not self.radio:
            return True
            
        if ch in '+=':
            vol = self.radio.volume_up()
            self.log(f"Volume: {vol}/15")
            
        elif ch == '-':
            vol = self.radio.volume_down()
            self.log(f"Volume: {vol}/15")
            
        elif ch in '>.':
            self.preset_idx = (self.preset_idx + 1) % len(PRESETS)
            freq, name = PRESETS[self.preset_idx]
            self.radio.set_frequency(freq)
            self.log(f"Preset {self.preset_idx+1}: {freq/100:.1f} MHz - {name}")
            
        elif ch in '<,':
            self.preset_idx = (self.preset_idx - 1) % len(PRESETS)
            freq, name = PRESETS[self.preset_idx]
            self.radio.set_frequency(freq)
            self.log(f"Preset {self.preset_idx+1}: {freq/100:.1f} MHz - {name}")
            
        elif ch in 'uU':
            self.log("Seeking up...")
            freq = self.radio.seek_up()
            self.log(f"Found: {freq/100:.1f} MHz")
            
        elif ch in 'dD':
            self.log("Seeking down...")
            freq = self.radio.seek_down()
            self.log(f"Found: {freq/100:.1f} MHz")
            
        elif ch in 'mM':
            self.radio._mute = not self.radio._mute
            self.radio.set_mute(self.radio._mute)
            self.log(f"{'Muted' if self.radio._mute else 'Unmuted'}")
            
        elif ch in 'bB':
            self.radio._bass_boost = not self.radio._bass_boost
            self.radio.set_bass_boost(self.radio._bass_boost)
            self.log(f"Bass boost {'ON' if self.radio._bass_boost else 'OFF'}")
            
        elif ch in 'sS':
            self.radio._mono = not self.radio._mono
            self.radio.set_mono(self.radio._mono)
            self.log(f"{'Mono' if self.radio._mono else 'Stereo'} mode")
            
        elif ch in 'rR':
            self.log("Checking RDS...")
            for _ in range(10):
                self.radio.check_rds()
                time.sleep(0.05)
            if self.rds.station_name:
                self.log(f"Station: {self.rds.station_name}")
                
        elif ch in 'pP':
            self.log("─── Presets ───")
            for i, (freq, name) in enumerate(PRESETS):
                marker = "►" if i == self.preset_idx else " "
                self.log(f" {marker} {i+1}. {freq/100:.1f} - {name}")
                
        elif ch in 'fF':
            self.log("Use number keys 1-9 for presets")
            
        elif ch.isdigit() and ch != '0':
            idx = int(ch) - 1
            if idx < len(PRESETS):
                self.preset_idx = idx
                freq, name = PRESETS[self.preset_idx]
                self.radio.set_frequency(freq)
                self.log(f"Preset {idx+1}: {freq/100:.1f} MHz - {name}")
                
        return True
        
    def run(self):
        """Main loop"""
        if not self.init_radio():
            self.log("Press any key to exit...")
            self.draw()
            self.stdscr.nodelay(False)
            self.stdscr.getch()
            return
            
        self.log("Ready! Use keys to control radio.")
        
        last_rds_check = 0
        running = True
        
        while running:
            # Check RDS periodically
            now = time.time()
            if self.radio and now - last_rds_check > 0.5:
                self.radio.check_rds()
                last_rds_check = now
                
            # Draw screen
            self.draw()
            
            # Handle input
            try:
                key = self.stdscr.getch()
                running = self.handle_input(key)
            except KeyboardInterrupt:
                running = False
                
        self.log("Goodbye!")
        self.draw()
        time.sleep(0.5)


def main(stdscr):
    ui = FMRadioUI(stdscr)
    ui.run()


if __name__ == "__main__":
    curses.wrapper(main)
