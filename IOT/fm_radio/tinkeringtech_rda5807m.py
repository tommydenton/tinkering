# SPDX-FileCopyrightText: Copyright (c) 2022 tinkeringtech for TinkeringTech LLC
# SPDX-License-Identifier: MIT
"""
CircuitPython/Blinka library for RDA5807M FM Radio chip
Used by ScoutMakes FM Radio Board

Ported/adapted for use with Raspberry Pi and Adafruit Blinka
"""

import time

# RDA5807M Register addresses
_RDA5807M_REG_CHIPID = 0x00
_RDA5807M_REG_CONFIG = 0x02
_RDA5807M_REG_TUNING = 0x03
_RDA5807M_REG_GPIO = 0x04
_RDA5807M_REG_VOLUME = 0x05
_RDA5807M_REG_I2S = 0x06
_RDA5807M_REG_BLEND = 0x07
_RDA5807M_REG_FREQ = 0x08
_RDA5807M_REG_STATUS = 0x0A
_RDA5807M_REG_RSSI = 0x0B
_RDA5807M_REG_RDSA = 0x0C
_RDA5807M_REG_RDSB = 0x0D
_RDA5807M_REG_RDSC = 0x0E
_RDA5807M_REG_RDSD = 0x0F


class RDSParser:
    """RDS (Radio Data System) parser for station info"""
    
    def __init__(self):
        self._text_callback = None
        self._station_name = ""
        self._radio_text = ""
        self._program_type = 0
        
    def attach_text_callback(self, callback):
        """Attach callback for RDS text updates"""
        self._text_callback = callback
        
    def process_data(self, block_a, block_b, block_c, block_d):
        """Process RDS data blocks"""
        # Group type
        group_type = (block_b >> 12) & 0x0F
        version = (block_b >> 11) & 0x01
        
        if group_type == 0:  # Basic tuning and switching
            # Program Service name (station name)
            segment = block_b & 0x03
            char1 = (block_d >> 8) & 0xFF
            char2 = block_d & 0xFF
            
            # Build station name
            pos = segment * 2
            name_list = list(self._station_name.ljust(8))
            if char1 >= 32 and char1 <= 126:
                name_list[pos] = chr(char1)
            if char2 >= 32 and char2 <= 126:
                name_list[pos + 1] = chr(char2)
            self._station_name = ''.join(name_list)
            
        elif group_type == 2:  # Radio Text
            segment = block_b & 0x0F
            if version == 0:  # Version A
                char1 = (block_c >> 8) & 0xFF
                char2 = block_c & 0xFF
                char3 = (block_d >> 8) & 0xFF
                char4 = block_d & 0xFF
                
                text_list = list(self._radio_text.ljust(64))
                pos = segment * 4
                for i, c in enumerate([char1, char2, char3, char4]):
                    if c >= 32 and c <= 126:
                        text_list[pos + i] = chr(c)
                self._radio_text = ''.join(text_list).rstrip()
                
                if self._text_callback:
                    self._text_callback(self._radio_text)
                    
    @property
    def station_name(self):
        return self._station_name.strip()
        
    @property
    def radio_text(self):
        return self._radio_text.strip()


class Radio:
    """RDA5807M FM Radio driver"""
    
    # Band definitions
    BAND_US_EU = 0  # 87-108 MHz
    BAND_JP = 1     # 76-91 MHz
    BAND_WORLD = 2  # 76-108 MHz
    BAND_EAST_EU = 3  # 65-76 MHz
    
    def __init__(self, i2c_device, freq=10110, volume=1):
        """
        Initialize the RDA5807M radio
        
        Args:
            i2c_device: I2CDevice instance for communication
            freq: Initial frequency in 10kHz units (e.g., 10110 = 101.1 MHz)
            volume: Initial volume (0-15)
        """
        self._i2c = i2c_device
        self._freq = freq
        self._volume = min(15, max(0, volume))
        self._band = self.BAND_US_EU
        self._mono = False
        self._mute = False
        self._bass_boost = False
        self._rds_parser = None
        
        # Register cache
        self._registers = [0] * 16
        
        # Initialize the chip
        self._init_chip()
        
    def _init_chip(self):
        """Initialize the RDA5807M chip"""
        # Soft reset and enable
        # Register 0x02: DHIZ=1, DMUTE=1, MONO=0, BASS=0, SEEKUP=0, SEEK=0, SKMODE=0, CLK_MODE=000, RDS_EN=1, NEW_METHOD=0, SOFT_RESET=1, ENABLE=1
        config = 0xC00D  # Enable RDS, soft reset, enable chip
        self._write_register(0x02, config)
        time.sleep(0.1)
        
        # Clear soft reset
        config = 0xC005  # Enable RDS, enable chip (no reset)
        self._write_register(0x02, config)
        
        # Set initial frequency
        self.set_frequency(self._freq)
        
        # Set initial volume
        self.set_volume(self._volume)
        
    def _write_register(self, reg, value):
        """Write a 16-bit value to a register"""
        data = bytes([reg, (value >> 8) & 0xFF, value & 0xFF])
        with self._i2c:
            self._i2c.write(data)
            
    def _read_registers(self, start_reg=0x0A, count=6):
        """Read multiple 16-bit registers starting from start_reg"""
        result = bytearray(count * 2)
        with self._i2c:
            self._i2c.readinto(result)
        
        registers = []
        for i in range(count):
            registers.append((result[i*2] << 8) | result[i*2 + 1])
        return registers
        
    def _freq_to_channel(self, freq):
        """Convert frequency (in 10kHz units) to channel number"""
        # Channel spacing is 100kHz (USA/Europe)
        # Channel = (Freq - 87MHz) / 100kHz
        if self._band == self.BAND_US_EU:
            base_freq = 8700  # 87.0 MHz in 10kHz units
        elif self._band == self.BAND_JP:
            base_freq = 7600  # 76.0 MHz
        else:
            base_freq = 7600
            
        return (freq - base_freq) // 10
        
    def _channel_to_freq(self, channel):
        """Convert channel number to frequency (in 10kHz units)"""
        if self._band == self.BAND_US_EU:
            base_freq = 8700
        elif self._band == self.BAND_JP:
            base_freq = 7600
        else:
            base_freq = 7600
            
        return base_freq + (channel * 10)
        
    def set_frequency(self, freq):
        """
        Set the radio frequency
        
        Args:
            freq: Frequency in 10kHz units (e.g., 10110 = 101.1 MHz)
        """
        self._freq = freq
        channel = self._freq_to_channel(freq)
        
        # Register 0x03: CHAN[9:0], DIRECT_MODE, TUNE, BAND[1:0], SPACE[1:0]
        # TUNE=1 to start tuning, BAND=00 (US/EU), SPACE=00 (100kHz)
        tune_reg = ((channel & 0x3FF) << 6) | 0x10 | (self._band << 2)
        self._write_register(0x03, tune_reg)
        
        time.sleep(0.1)  # Wait for tuning
        
    def get_frequency(self):
        """Get current frequency in 10kHz units"""
        regs = self._read_registers(0x0A, 2)
        channel = regs[0] & 0x03FF
        return self._channel_to_freq(channel)
        
    def set_volume(self, volume):
        """
        Set volume level
        
        Args:
            volume: Volume level 0-15
        """
        self._volume = min(15, max(0, volume))
        
        # Register 0x05: bits 3:0 are volume
        vol_reg = 0x84D0 | self._volume  # INT_MODE=1, SEEKTH=default, VOLUME
        self._write_register(0x05, vol_reg)
        
    def get_volume(self):
        """Get current volume level"""
        return self._volume
        
    def volume_up(self):
        """Increase volume by 1"""
        if self._volume < 15:
            self.set_volume(self._volume + 1)
        return self._volume
        
    def volume_down(self):
        """Decrease volume by 1"""
        if self._volume > 0:
            self.set_volume(self._volume - 1)
        return self._volume
        
    def set_band(self, band):
        """
        Set frequency band
        
        Args:
            band: "FM" for US/EU (87-108), "JP" for Japan (76-91)
        """
        if band.upper() == "FM" or band.upper() == "US" or band.upper() == "EU":
            self._band = self.BAND_US_EU
        elif band.upper() == "JP":
            self._band = self.BAND_JP
        else:
            self._band = self.BAND_US_EU
            
        # Re-tune with new band setting
        self.set_frequency(self._freq)
        
    def set_mute(self, mute):
        """Enable or disable mute"""
        self._mute = mute
        # Update config register
        config = 0xC005 if not mute else 0x8005
        self._write_register(0x02, config)
        
    def set_mono(self, mono):
        """Force mono mode"""
        self._mono = mono
        config = 0xC005
        if mono:
            config |= 0x2000  # Set MONO bit
        if self._mute:
            config &= ~0x4000  # Clear DMUTE bit
        self._write_register(0x02, config)
        
    def set_bass_boost(self, enable):
        """Enable bass boost"""
        self._bass_boost = enable
        config = 0xC005
        if enable:
            config |= 0x1000  # Set BASS bit
        if self._mono:
            config |= 0x2000
        if self._mute:
            config &= ~0x4000
        self._write_register(0x02, config)
        
    def seek_up(self):
        """Seek to next station up"""
        config = 0xC305  # SEEKUP=1, SEEK=1
        self._write_register(0x02, config)
        time.sleep(0.5)
        
        # Wait for seek to complete
        for _ in range(20):
            regs = self._read_registers()
            if regs[0] & 0x4000:  # STC (Seek/Tune Complete)
                break
            time.sleep(0.1)
            
        # Clear seek bit
        self._write_register(0x02, 0xC005)
        
        # Get new frequency
        self._freq = self.get_frequency()
        return self._freq
        
    def seek_down(self):
        """Seek to next station down"""
        config = 0xC105  # SEEKUP=0, SEEK=1
        self._write_register(0x02, config)
        time.sleep(0.5)
        
        # Wait for seek to complete
        for _ in range(20):
            regs = self._read_registers()
            if regs[0] & 0x4000:  # STC
                break
            time.sleep(0.1)
            
        # Clear seek bit
        self._write_register(0x02, 0xC005)
        
        self._freq = self.get_frequency()
        return self._freq
        
    def get_rssi(self):
        """Get received signal strength indicator (0-127)"""
        regs = self._read_registers(0x0A, 2)
        return (regs[1] >> 9) & 0x7F
        
    def is_stereo(self):
        """Check if current station is stereo"""
        regs = self._read_registers()
        return bool(regs[0] & 0x0400)
        
    def is_tuned(self):
        """Check if tuning is complete"""
        regs = self._read_registers()
        return bool(regs[0] & 0x4000)
        
    def get_rds_data(self):
        """
        Get RDS data if available
        
        Returns:
            Tuple of (block_a, block_b, block_c, block_d) or None
        """
        regs = self._read_registers(0x0A, 6)
        
        # Check RDS ready bit
        if regs[0] & 0x8000:  # RDSR
            return (regs[2], regs[3], regs[4], regs[5])
        return None
        
    def attach_rds_parser(self, parser):
        """Attach RDS parser instance"""
        self._rds_parser = parser
        
    def check_rds(self):
        """Check and process RDS data"""
        if self._rds_parser:
            data = self.get_rds_data()
            if data:
                self._rds_parser.process_data(*data)
                return True
        return False
        
    def get_status(self):
        """Get radio status as dictionary"""
        freq = self.get_frequency()
        freq_mhz = freq / 100.0
        
        return {
            'frequency': freq,
            'frequency_mhz': freq_mhz,
            'volume': self._volume,
            'rssi': self.get_rssi(),
            'stereo': self.is_stereo(),
            'mute': self._mute,
            'bass_boost': self._bass_boost,
        }
        
    def soft_reset(self):
        """Perform soft reset of the chip"""
        self._write_register(0x02, 0xC00D)
        time.sleep(0.1)
        self._write_register(0x02, 0xC005)
        self.set_frequency(self._freq)
        self.set_volume(self._volume)
