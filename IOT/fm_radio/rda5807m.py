#!/usr/bin/env python3
"""
RDA5807M FM Radio Driver - Fixed for Index Mode (0x11)
For ScoutMakes FM Radio Board on Raspberry Pi

Uses index mode I2C: send register address before data
"""

import time

class RDSParser:
    """RDS (Radio Data System) parser for station info"""
    
    def __init__(self):
        self._text_callback = None
        self._station_name = "        "
        self._radio_text = ""
        
    def attach_text_callback(self, callback):
        self._text_callback = callback
        
    def process_data(self, block_a, block_b, block_c, block_d):
        """Process RDS data blocks"""
        group_type = (block_b >> 12) & 0x0F
        
        if group_type == 0:  # Station name
            segment = block_b & 0x03
            char1 = (block_d >> 8) & 0xFF
            char2 = block_d & 0xFF
            
            name_list = list(self._station_name)
            pos = segment * 2
            if 32 <= char1 <= 126:
                name_list[pos] = chr(char1)
            if 32 <= char2 <= 126:
                name_list[pos + 1] = chr(char2)
            self._station_name = ''.join(name_list)
            
        elif group_type == 2:  # Radio Text
            segment = block_b & 0x0F
            chars = [
                (block_c >> 8) & 0xFF,
                block_c & 0xFF,
                (block_d >> 8) & 0xFF,
                block_d & 0xFF,
            ]
            text = ''.join(chr(c) if 32 <= c <= 126 else ' ' for c in chars)
            
            if self._text_callback and text.strip():
                self._text_callback(text)
                
    @property
    def station_name(self):
        return self._station_name.strip()


class Radio:
    """RDA5807M FM Radio driver using index mode I2C"""
    
    ADDR = 0x11
    
    def __init__(self, i2c, freq=10110, volume=5):
        """
        Initialize radio
        
        Args:
            i2c: busio.I2C instance (unlocked)
            freq: Frequency in 10kHz units (10110 = 101.1 MHz)
            volume: Volume 0-15
        """
        self._i2c = i2c
        self._freq = freq
        self._volume = min(15, max(0, volume))
        self._mute = False
        self._bass = False
        self._mono = False
        self._rds = None
        
        self._init_chip()
        
    def _write_reg(self, reg, value):
        """Write 16-bit value to register"""
        while not self._i2c.try_lock():
            pass
        try:
            data = bytes([reg, (value >> 8) & 0xFF, value & 0xFF])
            self._i2c.writeto(self.ADDR, data)
        finally:
            self._i2c.unlock()
            
    def _read_regs(self, start_reg, count):
        """Read count 16-bit registers starting at start_reg"""
        while not self._i2c.try_lock():
            pass
        try:
            # Send register address
            self._i2c.writeto(self.ADDR, bytes([start_reg]))
            # Read data
            result = bytearray(count * 2)
            self._i2c.readfrom_into(self.ADDR, result)
        finally:
            self._i2c.unlock()
            
        regs = []
        for i in range(count):
            regs.append((result[i*2] << 8) | result[i*2 + 1])
        return regs
        
    def _init_chip(self):
        """Initialize the RDA5807M"""
        # Soft reset
        self._write_reg(0x02, 0xC00D)
        time.sleep(0.1)
        
        # Enable: DHIZ=1, DMUTE=1, RDS_EN=1, ENABLE=1
        self._write_reg(0x02, 0xC005)
        time.sleep(0.1)
        
        # Set frequency and volume
        self.set_frequency(self._freq)
        self.set_volume(self._volume)
        
    def _get_reg02(self):
        """Build register 0x02 value based on current settings"""
        # DHIZ=1, DMUTE=!mute, MONO, BASS, RDS_EN=1, ENABLE=1
        val = 0x8001  # DHIZ + ENABLE
        if not self._mute:
            val |= 0x4000  # DMUTE
        if self._mono:
            val |= 0x2000  # MONO
        if self._bass:
            val |= 0x1000  # BASS
        val |= 0x0004  # RDS_EN
        return val
        
    def set_frequency(self, freq):
        """Set frequency in 10kHz units (e.g., 10110 = 101.1 MHz)"""
        self._freq = freq
        freq_mhz = freq / 100.0
        channel = int((freq_mhz - 87.0) * 10)
        
        # Reg 0x03: CHAN << 6 | TUNE | BAND | SPACE
        reg_03 = (channel << 6) | 0x10  # TUNE=1, BAND=0, SPACE=0
        self._write_reg(0x03, reg_03)
        
        time.sleep(0.1)
        
        # Clear TUNE bit
        reg_03 = (channel << 6) | 0x00
        self._write_reg(0x03, reg_03)
        
    def get_frequency(self):
        """Get current frequency in 10kHz units"""
        regs = self._read_regs(0x0A, 1)
        channel = regs[0] & 0x03FF
        freq_mhz = 87.0 + (channel * 0.1)
        return int(freq_mhz * 100)
        
    def set_volume(self, volume):
        """Set volume 0-15"""
        self._volume = min(15, max(0, volume))
        # Reg 0x05: INT_MODE=1, LNA_PORT=10, volume in bits 3:0
        reg_05 = 0x84D0 | self._volume
        self._write_reg(0x05, reg_05)
        
    def get_volume(self):
        return self._volume
        
    def volume_up(self):
        if self._volume < 15:
            self.set_volume(self._volume + 1)
        return self._volume
        
    def volume_down(self):
        if self._volume > 0:
            self.set_volume(self._volume - 1)
        return self._volume
        
    def set_mute(self, mute):
        self._mute = mute
        self._write_reg(0x02, self._get_reg02())
        
    def set_mono(self, mono):
        self._mono = mono
        self._write_reg(0x02, self._get_reg02())
        
    def set_bass_boost(self, bass):
        self._bass = bass
        self._write_reg(0x02, self._get_reg02())
        
    def seek_up(self):
        """Seek to next station up"""
        # SEEKUP=1, SEEK=1
        val = self._get_reg02() | 0x0300
        self._write_reg(0x02, val)
        
        time.sleep(0.3)
        
        # Wait for STC
        for _ in range(20):
            regs = self._read_regs(0x0A, 1)
            if regs[0] & 0x4000:  # STC
                break
            time.sleep(0.1)
            
        # Clear seek
        self._write_reg(0x02, self._get_reg02())
        
        self._freq = self.get_frequency()
        return self._freq
        
    def seek_down(self):
        """Seek to next station down"""
        # SEEKUP=0, SEEK=1
        val = self._get_reg02() | 0x0100
        self._write_reg(0x02, val)
        
        time.sleep(0.3)
        
        for _ in range(20):
            regs = self._read_regs(0x0A, 1)
            if regs[0] & 0x4000:
                break
            time.sleep(0.1)
            
        self._write_reg(0x02, self._get_reg02())
        
        self._freq = self.get_frequency()
        return self._freq
        
    def get_rssi(self):
        """Get signal strength 0-127"""
        regs = self._read_regs(0x0B, 1)
        return (regs[0] >> 9) & 0x7F
        
    def is_stereo(self):
        regs = self._read_regs(0x0A, 1)
        return bool(regs[0] & 0x0400)
        
    def get_rds_data(self):
        """Get RDS data if available"""
        regs = self._read_regs(0x0A, 6)
        if regs[0] & 0x8000:  # RDSR
            return (regs[2], regs[3], regs[4], regs[5])
        return None
        
    def attach_rds(self, rds):
        self._rds = rds
        
    def check_rds(self):
        if self._rds:
            data = self.get_rds_data()
            if data:
                self._rds.process_data(*data)
                return True
        return False
        
    def get_status(self):
        """Get status dict"""
        freq = self.get_frequency()
        return {
            'frequency': freq,
            'frequency_mhz': freq / 100.0,
            'volume': self._volume,
            'rssi': self.get_rssi(),
            'stereo': self.is_stereo(),
            'mute': self._mute,
            'bass_boost': self._bass,
            'mono': self._mono,
        }
