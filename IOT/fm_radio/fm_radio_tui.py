#!/usr/bin/env python3
"""
ScoutMakes FM Radio - Curses Interface
Fixed menu at top, scrolling log below
Uses index mode I2C for RDA5807

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
import busio
import rda5807m

# Fort Worth area FM stations (frequency in 10kHz units)
PRESETS = [
    (8870, "KTCU 88.7"),      # TCU College Radio
    (9010, "KERA 90.1"),      # NPR
    (9170, "KKXT 91.7"),      # Indie/AAA
    (9250, "KZPS 92.5"),      # Lone Star Classic Rock
    (9710, "KEGL 97.1"),      # The Eagle Rock
    (9870, "KLUV 98.7"),      # Classic Hits 60s/70s/80s
    (10030, "KJKK 100.3"),    # Jack FM
    (10210, "KDGE 102.1"),    # Star 102.1 AC
    (10610, "KHKS 106.1"),    # KISS FM Top 40
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
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
        
        self.stdscr.nodelay(True)
        self.stdscr.timeout(100)
        
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
            i2c = busio.I2C(board.SCL, board.SDA)
            
            # Check for device
            while not i2c.try_lock():
                pass
            devices = i2c.scan()
            i2c.unlock()
            
            if 0x11 not in devices:
                self.log("✗ FM Radio not found at 0x11")
                self.log(f"  Found: {[hex(d) for d in devices]}")
                return False
                
            self.log("✓ FM Radio found at 0x11")
            
        except Exception as e:
            self.log(f"✗ I2C error: {e}")
            return False
            
        self.rds = rda5807m.RDSParser()
        self.rds.attach_text_callback(self.rds_callback)
        
        freq, name = PRESETS[self.preset_idx]
        self.log(f"Tuning to {freq/100:.1f} MHz ({name})...")
        
        try:
            self.radio = rda5807m.Radio(i2c, freq, 8)
            self.radio.attach_rds(self.rds)
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
        
        # Minimum width check
        if width < 50:
            self.stdscr.addstr(0, 0, "Terminal too narrow!")
            return
            
        # Clear header area
        for i in range(11):
            self.stdscr.move(i, 0)
            self.stdscr.clrtoeol()
            
        # Title bar
        title = " ScoutMakes FM Radio "
        self.stdscr.attron(curses.color_pair(6) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * min(width, 200))
        self.stdscr.addstr(0, max(0, (width - len(title)) // 2), title[:width-1])
        self.stdscr.attroff(curses.color_pair(6) | curses.A_BOLD)
        
        if self.radio:
            status = self.radio.get_status()
            freq_mhz = status['frequency_mhz']
            
            # Find preset name
            preset_name = ""
            for i, (freq, name) in enumerate(PRESETS):
                if abs(freq - status['frequency']) < 10:
                    preset_name = name
                    self.preset_idx = i
                    break
                    
            # Frequency display
            self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            freq_str = f"{freq_mhz:5.1f} MHz"
            self.stdscr.addstr(2, 2, freq_str)
            self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            if preset_name:
                self.stdscr.addstr(2, 14, f"- {preset_name}"[:width-15])
            
            # Volume bar
            vol = status['volume']
            vol_bar = "█" * vol + "░" * (15 - vol)
            vol_str = f"Vol: [{vol_bar}] {vol:2d}/15"
            self.stdscr.addstr(3, 2, vol_str[:width-3])
            
            # Status indicators row
            col = 2
            
            if status['stereo']:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(4, col, "STEREO")
                self.stdscr.attroff(curses.color_pair(2))
            else:
                self.stdscr.attron(curses.color_pair(3))
                self.stdscr.addstr(4, col, "MONO  ")
                self.stdscr.attroff(curses.color_pair(3))
            col += 8
            
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
            
            if status['mute']:
                self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                self.stdscr.addstr(4, col, "MUTED")
                self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                col += 7
                
            if status['bass_boost']:
                self.stdscr.attron(curses.color_pair(2))
                self.stdscr.addstr(4, col, "BASS+")
                self.stdscr.attroff(curses.color_pair(2))
                
            # RDS text
            if self.rds and self.rds.station_name:
                self.stdscr.attron(curses.color_pair(5))
                self.stdscr.addstr(5, 2, f"RDS: {self.rds.station_name}"[:width-3])
                self.stdscr.attroff(curses.color_pair(5))
        else:
            self.stdscr.attron(curses.color_pair(4))
            self.stdscr.addstr(2, 2, "Radio not initialized")
            self.stdscr.attroff(curses.color_pair(4))
            
        # Menu separator and commands
        self.stdscr.addstr(7, 0, "─" * (width-1))
        menu1 = " +/- Vol  >/< Preset  u/d Seek  1-9 Jump"
        menu2 = " m Mute   b Bass      s Stereo  p List  q Quit"
        self.stdscr.addstr(8, 1, menu1[:width-2])
        self.stdscr.addstr(9, 1, menu2[:width-2])
        self.stdscr.addstr(10, 0, "─" * (width-1))
        
    def draw_log(self):
        """Draw scrolling log area"""
        height, width = self.stdscr.getmaxyx()
        log_start = 11
        log_height = height - log_start - 1
        
        if log_height <= 0:
            return
            
        visible_lines = self.log_lines[-log_height:]
        
        for i, line in enumerate(visible_lines):
            y = log_start + i
            if y < height - 1:
                self.stdscr.move(y, 0)
                self.stdscr.clrtoeol()
                self.stdscr.addstr(y, 0, line[:width-1])
                
    def draw(self):
        """Draw entire screen"""
        try:
            self.draw_header()
            self.draw_log()
            self.stdscr.refresh()
        except curses.error:
            pass
            
    def tune_preset(self, idx):
        """Tune to a preset by index"""
        if 0 <= idx < len(PRESETS):
            self.preset_idx = idx
            freq, name = PRESETS[idx]
            self.radio.set_frequency(freq)
            self.log(f"Preset {idx+1}: {freq/100:.1f} MHz - {name}")
            
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
            self.tune_preset(self.preset_idx)
            
        elif ch in '<,':
            self.preset_idx = (self.preset_idx - 1) % len(PRESETS)
            self.tune_preset(self.preset_idx)
            
        elif ch in 'uU':
            self.log("Seeking up...")
            self.draw()
            freq = self.radio.seek_up()
            self.log(f"Found: {freq/100:.1f} MHz")
            
        elif ch in 'dD':
            self.log("Seeking down...")
            self.draw()
            freq = self.radio.seek_down()
            self.log(f"Found: {freq/100:.1f} MHz")
            
        elif ch in 'mM':
            self.radio._mute = not self.radio._mute
            self.radio.set_mute(self.radio._mute)
            self.log(f"{'Muted' if self.radio._mute else 'Unmuted'}")
            
        elif ch in 'bB':
            self.radio._bass = not self.radio._bass
            self.radio.set_bass_boost(self.radio._bass)
            self.log(f"Bass boost {'ON' if self.radio._bass else 'OFF'}")
            
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
                
        elif ch.isdigit() and ch != '0':
            idx = int(ch) - 1
            if idx < len(PRESETS):
                self.tune_preset(idx)
                
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
            now = time.time()
            if self.radio and now - last_rds_check > 0.5:
                self.radio.check_rds()
                last_rds_check = now
                
            self.draw()
            
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
