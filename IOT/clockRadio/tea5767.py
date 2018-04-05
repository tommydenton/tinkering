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
GPIO.setmode(GPIO.BOARD)

# One lead each to GPI26 (pin37) and GPI20 (pin38)
# Buttons for changing Stations, common lead of ground

pin_tlm = 26              # pin37 = GPI26 (left button - Lower Freq)
pin_tlp = 20               # pin38 = GPI20 (right button - Higher Freq)


# set the appropriate GPIO pin as inputs with Pull-Up resistors
GPIO.setup(pin_tlm, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pin_tlp, GPIO.IN, pull_up_down=GPIO.PUD_UP)


bus = smbus.SMBus(1)        # novejsi varianta RasPi (512MB)
#bus = smbus.SMBus(0)       # starsi varianta RasPi (256MB)


# ================================================
# subroutine for the prime setting of the desired frequency
def nastav_f(freq):

  if (freq >= 87.5 and freq <= 108):  # when the frequency is within the allowed intervals, write to the circuit

    # frequency to two bytes (according to application instructions)
    freq14bit = int(4 * (freq * 1000000 + 225000)/32768)
    freqH = int(freq14bit / 256 )
    freqL = freq14bit & 0xFF

                                 # Byte bit descriptions - See. catalog sheet
    bajt0 = 0x60                 # I2C address of the circuit
    bajt1 = freqH                # 1.bajt (MUTE bit ; frequency H)
    bajt2 = freqL                # 2.bajt (frequency L)
    bajt3 = 0b10110000           # 3.bajt (SUD  ;  SSL1,SSL2  ;  HLSI  ;  MS,MR,ML  ;  SWP1)
    bajt4 = 0b00010000           # 4.bajt (SWP2 ; STBY ;  BL ; XTAL ; SMUTE ; HCC ; SNC ; SI)
    bajt5 = 0b00000000           # 5.bajt (PLREFF  ;  DTC  ;  0;0;0;0;0;0)

    blokdat=[ bajt2 , bajt3 , bajt4 , bajt5 ]
    bus.write_i2c_block_data( bajt0 , bajt1 , blokdat )   # set the new frequency to the circuit

    time.sleep(0.1)                 #It took a moment to assess the strength of the signal

    bajt1r = bus.read_byte(bajt0)   # nacist first byte (must be cleaned separately)
    data = bus.read_i2c_block_data( bajt0 , bajt1 )     # The precision of the data from the detection circuit will flatten the signal
    data[0] = bajt1r                # replace the first byte pretense with a self-declared value

    print "frekvence= " + str(freq) + "MHz" , "\tDATA: " + str(data[0:5]) + "\t(signal strength:" + str(data[3]>>4) + ")"

  return(freq)

# ================================================
# Subroutine to find the closest station from the specified frequency
def sken(freq , smer):

  if (sys.argv[1] == "-v"):             # when I report ALL MUCH frequencies ...
    jen_1_freq = False                  # only one frequency is being searched
    try:
      adc_limit = int(sys.argv[2])      # find the parameter of the minimal level of AD for the autosken
    except:
      adc_limit=7                       # when it fails, it is automatically set to 7

  elif (sys.argv[1] == "-t"):           # v rezimu hledani pomoci tlacitek
    jen_1_freq = True                   #    se hleda jen jedna frekvence
    try:
      adc_limit = int(sys.argv[2])      # zjisti parametr minimalni urovne AD prevodniku pro autosken
    except:
      adc_limit=7                       # kdyz chybi, nastavi se automaticky na 7

  else:                                 # kdyz je nastaveno vyhledani POUZE PRVNI silne frekvence ...
    jen_1_freq = True                   #    hleda se jen jedna frekvence
    try:
      adc_limit = int(sys.argv[3])      # zjisti parametr minimalni urovne AD prevodniku pro autosken
    except:
      adc_limit=7                       # kdyz chybi, nastavi se automaticky na 7


  if (adc_limit > 15 or adc_limit < 0): # vyhodnoceni, jestli je zadany limit v mezi 0 az 15
    adc_limit = 7                       # kdyz je mimo, nastavi se automaticky na 7

  if (sys.argv[1] == "-v"):             # pri funkci automatickeho prohledani celeho pasma vytiskne info
    print "Zobrazuji frekvence, ktere maji silu signalu alespon " + str(adc_limit)


# main loop with control if the frequency is within the allowed intervals
  while (freq >= 87.5 and freq <= 108):  # kdyz je frekvence mimo povoleny rozsah, smycka se ukonci

    if(smer == True):    # podle smeru skenovani se bud pridava nebo ubira 100kHz
      freq= freq + 0.1
    else:
      freq= freq - 0.1

    # prepocet frekvence na dva bajty (podle aplikacnich pokynu)
    freq14bit = int(4 * (freq * 1000000 + 225000)/32768)
    freqH = int(freq14bit / 256 )
    freqL = freq14bit & 0xFF

    mutebit = 0b00000000         # pri vyhledavani zapnout zvuk (huci/sumi/piska jako normalni radio pri ladeni)
#    mutebit = 0b10000000        # pri vyhledavani vypnout hlasitost

                                 # popisy jednotlivych bitu v bajtech - viz. katalogovy list
    bajt0 = 0x60                 # I2C adresa obvodu
    bajt1 = freqH | mutebit      # 1.bajt (MUTE bit ; frekvence H)
    bajt2 = freqL                # 2.bajt (frekvence L)
    bajt3 = 0b10110000           # 3.bajt (SUD  ;  SSL1,SSL2  ;  HLSI  ;  MS,MR,ML  ;  SWP1)
    bajt4 = 0b00010000           # 4.bajt (SWP2 ; STBY ;  BL ; XTAL ; SMUTE ; HCC ; SNC ; SI)
    bajt5 = 0b00000000           # 5.bajt (PLREFF  ;  DTC  ;  0;0;0;0;0;0)

    blokdat=[ bajt2 , bajt3 , bajt4 , bajt5 ]

    # preladeni na novou frekvenci
    bus.write_i2c_block_data( bajt0 , bajt1 , blokdat )

    time.sleep(0.05)  # mezi jednotlivymi frekvencemi chvili pockej, nez se vyhodnoti sila signalu

    # precteni obsahu vsech registru
    bajt1r = bus.read_byte(bajt0)                       # prvni bajt se musi cist samostatne
    data = bus.read_i2c_block_data( bajt0 , bajt1 )     # nacteni vsech bajtu z obvodu
    data[0] = bajt1r                                    # prvni bajt se nahradi samostatne nactenou hodnotou


    sila = data[3] >> 4   # v nejvyssich 4 bitech ctvrteho baju (data[3]) je pri cteni registru uroven signalu

    if (sila >= adc_limit):   # minimalni sila signalu, ktera bude povazovan za naladenou stanici (0 az 15)
      print "f= " + str(freq) + "MHz" , "\tDATA:" + str(data[0:5]) + "\t(Sila signalu: " + str(sila) + ")"

      if (mutebit == 0b10000000):   # zruseni pripadneho MUTE bitu po nalezeni stanice
        bajt1 = bajt1 & 0b01111111
        bus.write_i2c_block_data( bajt0 , bajt1  , blokdat )

      if (jen_1_freq == True):  # kdyz se hleda jen jedna nejblizsi frekvence, tak se po nalezeni ukonci smycka while
        break

  if (freq > 108):                      # kdyz prejede pres horni konec pasma ...
    freq=108                            # ... tak se na ten konec vrati ...
    print "dosazen horni konec pasma"   # a zahlasi, ze je na konci
  if (freq < 87.5):                     # kdyz prejede pod spodni konec pasma ...
    freq=87.5                           # ... tak se na ten konec vrati ...
    print "dosazen spodni konec pasma"  # a zahlasi, ze je na konci
  return (freq)




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
