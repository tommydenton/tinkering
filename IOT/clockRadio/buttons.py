#!/usr/bin/python
# -*- encoding: utf-8 -*-

# ovladani FM prijimace TEA5767 pres I2C komunikaci
# posledni uprava 9.6.2013
# Translated by Thomas Denton using Google Translate

import smbus               # I^2C operations
import time                # Time operations
import sys                 # Interact with the Command Line
import RPi.GPIO as GPIO    # GPI operations


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# One lead each to GPIO26 (pin37) and GPIO20 (pin38)
# Buttons for changing Stations, common lead of ground

pin_tlm = 26              # pin37 = GPIO26 (left button - Lower Freq)
pin_tlp = 20               # pin38 = GPIO20 (right button - Higher Freq)


# set the appropriate GPIO pin as inputs with Pull-Up resistors
GPIO.setup(pin_tlm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_tlp, GPIO.IN, pull_up_down=GPIO.PUD_UP)


bus = smbus.SMBus(1)        # novejsi varianta RasPi (512MB)
#bus = smbus.SMBus(0)       # starsi varianta RasPi (256MB)


# ================================================
# subroutine for pushbutton stations
def tlacitka():

  tl_minus = 0
  tl_plus  = 0

  print "... search ->>->>->>"
  freq = sken(97.1, True)     # pri spusteni podprogramu se vyhleda prvni stanice zdola


# When starting the subroutine, the first station is searched from below
  while ((tl_minus == 0) or (tl_plus == 0)):  # when both are pushed or when missing, the loop will terminate

    tl_minus = GPIO.input(pin_tlm)            # read status of GPIO pins
    tl_plus  = GPIO.input(pin_tlp)

    if (tl_plus == 1):           # while pushing the PLUS button is looking for the closest higher station
      print "... search ->>->>->>"
      time.sleep(0.5)
      if (tl_minus == 0):        # when the MINUS button is not pressed ...
        freq = sken(freq, True)  # search for the nearest frequency

    if (tl_minus == 1):          # pressing the MINUS button will search for the closest lower station
      print "... search <<-<<-<<-"
      time.sleep(0.5)
      if(tl_plus == 0):          # when the PLUS button is not pressed ...
        freq = sken(freq, False) # search for the closest frequency

    time.sleep(0.1)



    # ================================================
    # subroutine for switching preset stations using the buttons
def prepinac():

  tl_minus = 0
  tl_plus  = 0


    # manually create a list of stations and their frequency
  stanice = {}
  stanice[0] = [97.1 , "KEGL"]
  stanice[1] = [90.1 , "KERA"]
  stanice[2] = [91.7 , "KKXT"]
  stanice[3] = [92.5 , "KZPS"]
  stanice[4] = [93.3 , "KLIF"]
  stanice[5] = [97.1 , "KEGL"]
  stanice[6] = [98.7 , "KLUV"]
  stanice[7] = [100.3 , "KJKK"]
  stanice[8] = [102.1 , "KDGE"]
  stanice[9] = [102.9 , "KDMX"]
  stanice[10] = [103.3 , "KESN"]
  stanice[11] = [103.7 , "KVIL"]
  stanice[12] = [105.3 , "KRLD"]
  stanice[13] = [106.1 , "KHKS"]
  stanice[14] = [89.3 , "KNON"]

  # in the variable "float ([index] [0])" is the frequency of the station with the appropriate index
  # in the variable "[index] [1]" is the station name with the appropriate index


  pocet_stanic = len(stanice)

  index = 0                      # Set the frequency to the zero station when running the subroutine
  print stanice[index][1]
  nastav_f(stanice[index][0])

    # main loop for testing two spreader keys
  while ((tl_minus == 0) or (tl_plus == 0)):  # when both are pushed or when missing, the loop will terminate
    tl_minus = GPIO.input(pin_tlm)            # read status of GPIO pins
    tl_plus  = GPIO.input(pin_tlp)


    if (tl_plus == 1):                  # Press the PLUS button to switch to the next station in the list
      time.sleep(0.5)
      if (tl_minus == 0):               # when the MINUS button is not pressed ...
        index = index + 1               # ... moves the index to the next station
        if (index > (pocet_stanic-1)):  # when the index is higher than the number of stations ...
          index = 0                     # ... sets the index to the beginning of the list

        print stanice[index][1]
        nastav_f(stanice[index][0])     # set the frequency of the current station


    if (tl_minus == 1):                 # Press the MINUS button to switch to the previous station in the list
      time.sleep(0.5)
      if (tl_plus == 0):                # when the PLUS button is not pressed ...
        index = index - 1               # moves the index to the previous station
        if (index < 0):                 # when the index "under" under the first station ...
          index = (pocet_stanic-1)      # ... sets the index on the last station in the list

        print stanice[index][1]
        nastav_f(stanice[index][0])     # set the frequency of the current station

    time.sleep(0.1)



# ================================================
# start of the program - evaluation of the command line parameter
# ================================================

try:                        # if the first parameter is missing, the message is displayed
  parametr=sys.argv[1]
except:
  parametr=""

if (parametr=="-n"):        # prime setting of specific frequency
  try:
    freq= float(sys.argv[2])
  except:
    freq=0
  nastav_f(freq)


elif (parametr == "-sn"):    # automatic scanning "UP" from the specified frequency
  try:
    freq= float(sys.argv[2])
  except:
    freq=87.5                # If the parameter is missing or is faulty, the lower limit of the pass is set
  sken(freq, True)           # scan from specified frequency UP



elif (parametr == "-sd"):    # automatic scanning "DOWN" from entered frequency
  try:
    freq= float(sys.argv[2])
  except:
    freq=108                 # When the parameter is missing or is incorrect, the upper limit of the pass is set
  sken(freq, False )         # scan from specified frequency DOWN



elif (parametr == "-v"):     # automatic listing of all strong frequencies
  sken(87.5, True )          # scanned from the top of the TOP



elif (parametr == "-h0"):    # mute the volume
  bajt1 = bus.read_byte( 0x60 )
  bajt1 = bajt1 | 0b10000000
  bus.write_byte(0x60,bajt1)



elif (parametr == "-h1"):    # restore volume
  bajt1 = bus.read_byte( 0x60 )
  bajt1 = bajt1 & 0b01111111
  bus.write_byte(0x60,bajt1)



elif (parametr == "-t"):     # use the GPIO buttons to automatically search for the closest stations
  tlacitka()



elif (parametr == "-p"):     # Use the GPIO buttons to switch the preset stations
  prepinac()



else:                        # If the first parameter does not match the backend, the message appears
  print "pripustne parametry:"
  print "... -n fff.f       prime frequency setting"
  print "... -sn fff.f LL   find the nearest station above the specified frequency"
  print "... -sd fff.f LL   find the closest station below the specified frequency"
  print "... -v LL          automatically listing all strong frequencies"
  print "... -h0            Complete Mute Volume (MUTE)"
  print "... -h1            to restore the volume"
  print "... -t LL          search for help stations on GPIO ports"
  print "... -p             switching pre-defined help stations"
  print ""
  print "  fff.f = frequency in MHz. Allowable values are between 87.5 and 108"
  print "  LL    = the minimum signal strength (ADC_level) at which the signal is"
  print "          when searching automatically after a station (0 to 15)"
