#!/usr/bin/env python3
"""
RDA5807 FM Radio Debug Script - Fixed for Index Mode
Address 0x11 requires register index byte first
"""

import time
import board
import busio

RDA5807_ADDR = 0x11

def write_reg(i2c, reg, value):
    """Write 16-bit value to register using index mode"""
    data = bytes([reg, (value >> 8) & 0xFF, value & 0xFF])
    i2c.writeto(RDA5807_ADDR, data)
    print(f"    Wrote reg 0x{reg:02X} = 0x{value:04X}")

def read_regs(i2c, start_reg, count):
    """Read registers using index mode"""
    # Write register address to read from
    i2c.writeto(RDA5807_ADDR, bytes([start_reg]))
    # Read the data
    result = bytearray(count * 2)
    i2c.readfrom_into(RDA5807_ADDR, result)
    
    regs = []
    for i in range(count):
        regs.append((result[i*2] << 8) | result[i*2 + 1])
    return regs

def main():
    print("="*50)
    print("RDA5807 FM Radio Debug - Index Mode")
    print("="*50)
    
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
    
    # Check for address conflict with GPS at 0x10
    if 0x10 in devices:
        print(f"    NOTE: GPS also present at 0x10 (RDA5807 alt addr)")
        print(f"    Using 0x11 index mode to avoid conflict")
    
    print(f"\n[2] Soft reset...")
    # Reg 0x02: DHIZ=1, DMUTE=1, RDS_EN=1, SOFT_RESET=1, ENABLE=1
    write_reg(i2c, 0x02, 0xC00D)
    time.sleep(0.1)
    
    # Clear soft reset
    write_reg(i2c, 0x02, 0xC005)
    time.sleep(0.1)
    print("    Reset complete")
    
    print(f"\n[3] Reading status...")
    try:
        regs = read_regs(i2c, 0x0A, 2)
        print(f"    Reg 0x0A = 0x{regs[0]:04X}")
        print(f"    Reg 0x0B = 0x{regs[1]:04X}")
        rssi = (regs[1] >> 9) & 0x7F
        print(f"    RSSI = {rssi}")
    except Exception as e:
        print(f"    Read error: {e}")
    
    print(f"\n[4] Tuning to 101.1 MHz...")
    freq_mhz = 101.1
    channel = int((freq_mhz - 87.0) * 10)  # 141
    print(f"    Target: {freq_mhz} MHz = channel {channel}")
    
    # Reg 0x03: CHAN[9:0] << 6 | TUNE | BAND | SPACE
    # TUNE=1 (bit 4), BAND=00 (US/EU 87-108), SPACE=00 (100kHz)
    reg_03 = (channel << 6) | 0x10
    print(f"    Reg 0x03 = 0x{reg_03:04X}")
    
    write_reg(i2c, 0x03, reg_03)
    
    print(f"\n[5] Waiting for tune...")
    time.sleep(0.5)
    
    # Poll for STC (Seek/Tune Complete)
    for attempt in range(10):
        regs = read_regs(i2c, 0x0A, 2)
        stc = bool(regs[0] & 0x4000)
        if stc:
            break
        time.sleep(0.1)
    
    # Read final status
    channel_read = regs[0] & 0x03FF
    freq_read = 87.0 + (channel_read * 0.1)
    stereo = bool(regs[0] & 0x0400)
    rssi = (regs[1] >> 9) & 0x7F
    
    print(f"    STC (complete): {stc}")
    print(f"    Channel: {channel_read}")
    print(f"    Frequency: {freq_read:.1f} MHz")
    print(f"    Stereo: {stereo}")
    print(f"    RSSI: {rssi}")
    
    if abs(freq_read - freq_mhz) > 0.2:
        print(f"\n    ⚠ TUNING MISMATCH!")
        print(f"    Expected {freq_mhz} MHz, got {freq_read:.1f} MHz")
    else:
        print(f"\n    ✓ Tuned correctly!")
    
    print(f"\n[6] Setting volume...")
    # Reg 0x05: bits 3:0 = volume (0-15)
    # INT_MODE=1, LNA_PORT=10, other defaults
    volume = 10
    reg_05 = 0x84D0 | volume
    write_reg(i2c, 0x05, reg_05)
    print(f"    Volume set to {volume}/15")
    
    print(f"\n[7] Clear TUNE bit...")
    # Keep channel but clear TUNE bit
    reg_03_clear = (channel << 6) | 0x00
    write_reg(i2c, 0x03, reg_03_clear)
    
    i2c.unlock()
    
    print(f"\n" + "="*50)
    print("Plug headphones into the FM board's 3.5mm jack")
    print(f"You should hear {freq_mhz} MHz")
    print("="*50)
    
    # Interactive tuning test
    print("\nQuick tune test - enter frequencies to try:")
    print("(Enter 'q' to quit)")
    
    while True:
        try:
            inp = input("\nFrequency (e.g. 97.1): ").strip()
            if inp.lower() == 'q':
                break
            
            freq = float(inp)
            if freq < 87.0 or freq > 108.0:
                print("Must be between 87.0 and 108.0")
                continue
                
            while not i2c.try_lock():
                pass
            
            channel = int((freq - 87.0) * 10)
            reg_03 = (channel << 6) | 0x10
            write_reg(i2c, 0x03, reg_03)
            
            time.sleep(0.3)
            
            regs = read_regs(i2c, 0x0A, 2)
            channel_read = regs[0] & 0x03FF
            freq_read = 87.0 + (channel_read * 0.1)
            stereo = "Stereo" if (regs[0] & 0x0400) else "Mono"
            rssi = (regs[1] >> 9) & 0x7F
            
            # Clear tune bit
            write_reg(i2c, 0x03, (channel << 6) | 0x00)
            
            i2c.unlock()
            
            print(f"Tuned to {freq_read:.1f} MHz | {stereo} | RSSI: {rssi}")
            
        except ValueError:
            print("Invalid input")
        except KeyboardInterrupt:
            break
    
    print("\nDone!")

if __name__ == "__main__":
    main()
