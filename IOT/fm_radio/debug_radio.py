#!/usr/bin/env python3
"""
Simple FM Radio Debug Script
Tests basic communication with RDA5807
"""

import time
import board
import busio

# I2C address for RDA5807
RDA5807_ADDR = 0x11

def main():
    print("="*50)
    print("RDA5807 FM Radio Debug")
    print("="*50)
    
    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA)
    
    while not i2c.try_lock():
        pass
    
    print(f"\n[1] Scanning I2C bus...")
    devices = i2c.scan()
    print(f"    Found: {[hex(d) for d in devices]}")
    
    if RDA5807_ADDR not in devices:
        print(f"    ERROR: RDA5807 not found at 0x{RDA5807_ADDR:02x}")
        i2c.unlock()
        return
    
    print(f"    ✓ RDA5807 found at 0x{RDA5807_ADDR:02x}")
    
    # The RDA5807 has two I2C modes:
    # - Sequential access mode (address 0x10) - read/write registers in sequence
    # - Random access mode (address 0x11) - specify register address
    #
    # For sequential write starting at reg 0x02:
    # Just write bytes, they go to 0x02, 0x03, 0x04...
    #
    # For sequential read starting at reg 0x0A:
    # Just read bytes, they come from 0x0A, 0x0B, 0x0C...
    
    print(f"\n[2] Reading chip status...")
    
    # Read 12 bytes (6 registers starting at 0x0A)
    result = bytearray(12)
    try:
        i2c.readfrom_into(RDA5807_ADDR, result)
        print(f"    Raw: {result.hex()}")
        
        # Parse status register 0x0A
        reg_0a = (result[0] << 8) | result[1]
        print(f"    Reg 0x0A: 0x{reg_0a:04x}")
        print(f"      RDSR (RDS ready): {bool(reg_0a & 0x8000)}")
        print(f"      STC (Seek/Tune complete): {bool(reg_0a & 0x4000)}")
        print(f"      SF (Seek fail): {bool(reg_0a & 0x2000)}")
        print(f"      RDSS (RDS sync): {bool(reg_0a & 0x1000)}")
        print(f"      ST (Stereo): {bool(reg_0a & 0x0400)}")
        
        # Channel from 0x0A
        channel = reg_0a & 0x03FF
        freq_mhz = 87.0 + (channel * 0.1)
        print(f"      Channel: {channel} = {freq_mhz:.1f} MHz")
        
        # RSSI from 0x0B
        reg_0b = (result[2] << 8) | result[3]
        rssi = (reg_0b >> 9) & 0x7F
        print(f"    Reg 0x0B: 0x{reg_0b:04x}")
        print(f"      RSSI: {rssi}")
        
    except Exception as e:
        print(f"    ERROR reading: {e}")
    
    print(f"\n[3] Initializing radio...")
    
    # Write initialization sequence starting at register 0x02
    # Reg 0x02: DHIZ=1, DMUTE=1, MONO=0, BASS=0, RCLK=0, RCLK_DM=0, SEEKUP=0, 
    #           SEEK=0, SKMODE=0, CLK_MODE=000, RDS_EN=1, NEW_DM=0, SOFT_RESET=1, ENABLE=1
    # = 0xC00D for init with soft reset
    # Then 0xC005 to clear reset
    
    init_data = bytes([
        0xC0, 0x0D,  # Reg 0x02: Enable with soft reset
    ])
    
    try:
        i2c.writeto(RDA5807_ADDR, init_data)
        print("    Wrote soft reset")
        time.sleep(0.1)
        
        # Clear soft reset, keep enabled
        init_data = bytes([
            0xC0, 0x05,  # Reg 0x02: Enable, RDS on, no reset
        ])
        i2c.writeto(RDA5807_ADDR, init_data)
        print("    Cleared reset, radio enabled")
        time.sleep(0.1)
        
    except Exception as e:
        print(f"    ERROR writing: {e}")
        i2c.unlock()
        return
    
    print(f"\n[4] Tuning to 101.1 MHz...")
    
    # To tune: write to registers 0x02 and 0x03 together
    # Reg 0x02: same config
    # Reg 0x03: CHAN[9:6] in high byte, CHAN[5:0]|TUNE|BAND|SPACE in low byte
    #
    # For 101.1 MHz: channel = (101.1 - 87.0) / 0.1 = 141
    # TUNE=1, BAND=00 (US), SPACE=00 (100kHz)
    
    freq_mhz = 101.1
    channel = int((freq_mhz - 87.0) / 0.1)
    print(f"    Frequency: {freq_mhz} MHz, Channel: {channel}")
    
    # Reg 0x03 = (channel << 6) | 0x10  (TUNE=1, BAND=0, SPACE=0)
    reg_03 = (channel << 6) | 0x10
    
    tune_data = bytes([
        0xC0, 0x05,                    # Reg 0x02
        (reg_03 >> 8) & 0xFF, reg_03 & 0xFF,  # Reg 0x03
    ])
    
    try:
        i2c.writeto(RDA5807_ADDR, tune_data)
        print(f"    Wrote tune command: {tune_data.hex()}")
    except Exception as e:
        print(f"    ERROR: {e}")
        i2c.unlock()
        return
    
    print(f"\n[5] Waiting for tune to complete...")
    time.sleep(0.5)
    
    # Read status again
    result = bytearray(12)
    i2c.readfrom_into(RDA5807_ADDR, result)
    
    reg_0a = (result[0] << 8) | result[1]
    stc = bool(reg_0a & 0x4000)
    stereo = bool(reg_0a & 0x0400)
    channel_read = reg_0a & 0x03FF
    freq_read = 87.0 + (channel_read * 0.1)
    
    reg_0b = (result[2] << 8) | result[3]
    rssi = (reg_0b >> 9) & 0x7F
    
    print(f"    STC (tune complete): {stc}")
    print(f"    Tuned to: {freq_read:.1f} MHz")
    print(f"    Stereo: {stereo}")
    print(f"    RSSI: {rssi}")
    
    print(f"\n[6] Setting volume to 8...")
    
    # Volume is in reg 0x05 bits 3:0
    # Reg 0x05 = 0x84D0 | volume (INT_MODE=1, other defaults, volume)
    volume = 8
    reg_05 = 0x84D0 | volume
    
    # Need to write regs 0x02, 0x03, 0x04, 0x05 in sequence
    vol_data = bytes([
        0xC0, 0x05,                    # Reg 0x02
        (reg_03 >> 8) & 0xFF, reg_03 & 0xFF,  # Reg 0x03 (keep tune settings but clear TUNE bit)
        0x0A, 0x00,                    # Reg 0x04 (GPIO defaults)
        (reg_05 >> 8) & 0xFF, reg_05 & 0xFF,  # Reg 0x05
    ])
    
    # Actually, let's clear the TUNE bit in reg 0x03 after tuning
    reg_03_notune = (channel << 6) | 0x00  # TUNE=0
    vol_data = bytes([
        0xC0, 0x05,
        (reg_03_notune >> 8) & 0xFF, reg_03_notune & 0xFF,
        0x0A, 0x00,
        (reg_05 >> 8) & 0xFF, reg_05 & 0xFF,
    ])
    
    try:
        i2c.writeto(RDA5807_ADDR, vol_data)
        print(f"    Volume set to {volume}")
    except Exception as e:
        print(f"    ERROR: {e}")
    
    i2c.unlock()
    
    print(f"\n" + "="*50)
    print("Debug complete!")
    print("If tuned correctly, you should hear audio on the")
    print("FM board's 3.5mm headphone jack.")
    print("="*50)
    

if __name__ == "__main__":
    main()
