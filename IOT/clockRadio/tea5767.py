#!/usr/bin/python
# -*- encoding: utf-8 -*-

# ovladani FM prijimace TEA5767 pres I2C komunikaci
# posledni uprava 9.6.2013


import smbus               # operace s I2C
import time                # operace s casem (pauzy)
import sys                 # zjistovani parametru prikazove radky 
import RPi.GPIO as GPIO    # Ovladani GPIO vystupu v RasPi


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)   # cislovani podle hardwerovych pinu (1 az 26)

# tlacitka jsou rozpinaci, jeden spolecny vyvod maji na GND,
#   zbyle vyvody jsou zapojeny na GPIO7 (pin26) a GPIO8 (pin24)

pin_tlm = 26               # pin26 = GPIO7 (leve tlacitko - odecitani frekvence)
pin_tlp = 24               # pin24 = GPIO8 (prave tlacitko - pricitani frekvence)


# nastaveni prislusnych GPIO  pinu jako vstupy s Pull-Up odpory
GPIO.setup(pin_tlm, GPIO.IN, pull_up_down=GPIO.PUD_UP)    
GPIO.setup(pin_tlp, GPIO.IN, pull_up_down=GPIO.PUD_UP)


bus = smbus.SMBus(1)       # novejsi varianta RasPi (512MB)
#bus = smbus.SMBus(0)       # starsi varianta RasPi (256MB)


# ================================================
# podprogram pro prime nastaveni pozadovane frekvence
def nastav_f(freq):

  if (freq >= 87.5 and freq <= 108):  # kdyz je frekvence v pripustnych mezich, zapise se do obvodu

    # prepocet frekvence na dva bajty (podle aplikacnich pokynu)
    freq14bit = int(4 * (freq * 1000000 + 225000)/32768)
    freqH = int(freq14bit / 256 )
    freqL = freq14bit & 0xFF

                                 # popisy jednotlivych bitu v bajtech - viz. katalogovy list
    bajt0 = 0x60                 # I2C adresa obvodu
    bajt1 = freqH                # 1.bajt (MUTE bit ; frekvence H)
    bajt2 = freqL                # 2.bajt (frekvence L)
    bajt3 = 0b10110000           # 3.bajt (SUD  ;  SSL1,SSL2  ;  HLSI  ;  MS,MR,ML  ;  SWP1)
    bajt4 = 0b00010000           # 4.bajt (SWP2 ; STBY ;  BL ; XTAL ; SMUTE ; HCC ; SNC ; SI)
    bajt5 = 0b00000000           # 5.bajt (PLREFF  ;  DTC  ;  0;0;0;0;0;0)

    blokdat=[ bajt2 , bajt3 , bajt4 , bajt5 ]
    bus.write_i2c_block_data( bajt0 , bajt1 , blokdat )   # nastaveni nove frekvence do obvodu

    time.sleep(0.1)                 # chvili pockej, nez se vyhodnoti sila signalu

    bajt1r = bus.read_byte(bajt0)   # nacist prvni bajt (musi se cist samostatne)
    data = bus.read_i2c_block_data( bajt0 , bajt1 )     # precteni dat z obvodu pro zjisteni urovne signalu 
    data[0] = bajt1r                # nahradit prvni precteny bajt samostatne nactenou hodnotou

    print "frekvence= " + str(freq) + "MHz" , "\tDATA: " + str(data[0:5]) + "\t(Sila signalu:" + str(data[3]>>4) + ")"

  return(freq)

# ================================================
# podprogram pro vyhledavani nejblizsi stanice od zadane frekvence
def sken(freq , smer):

  if (sys.argv[1] == "-v"):             # kdyz se vypisuji VSECHNY silne frekvence ...
    jen_1_freq = False                  #     nehleda se jen jedna frekvence
    try:
      adc_limit = int(sys.argv[2])      # zjisti parametr minimalni urovne AD prevodniku pro autosken
    except:
      adc_limit=7                       # kdyz chybi, nastavi se automaticky na 7

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


  # hlavni smycka s kontrolou, jestli je frekvence v pripustnych mezich
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
# podprogram pro vyhledavani stanic pomoci tlacitek
def tlacitka():

  tl_minus = 0
  tl_plus  = 0
 
  print "... vyhledavani ->>->>->>"
  freq = sken(87.5, True)     # pri spusteni podprogramu se vyhleda prvni stanice zdola


  # hlavni smycka na testovani dvou rozpinacich tlacitek
  while ((tl_minus == 0) or (tl_plus == 0)):  # kdyz jsou obe stlacena, nebo kdyz chybi, smycka se ukonci

    tl_minus = GPIO.input(pin_tlm)            # cteni stavu tlacitek na GPIO pinech
    tl_plus  = GPIO.input(pin_tlp)

    if (tl_plus == 1):           # pri stisku PLUS tlacitka se hleda nejblizsi vyssi stanice
      print "... vyhledavani ->>->>->>"
      time.sleep(0.5)
      if (tl_minus == 0):        # kdyz neni stisknuto zaroven i MINUS tlacitko...
        freq = sken(freq, True)  # vyhledej nejblizsi vyssi frekvenci

    if (tl_minus == 1):          # pri stisku MINUS tlacitka se hleda nejblizsi nizsi stanice
      print "... vyhledavani <<-<<-<<-"
      time.sleep(0.5)
      if(tl_plus == 0):          # kdyz neni stisknuto zaroven i PLUS tlacitko...
        freq = sken(freq, False) # vyhledej nejblizsi nizsi frekvenci

    time.sleep(0.1)



# ================================================
# podprogram pro prepinani predvolenych stanic pomoci tlacitek
def prepinac():

  tl_minus = 0
  tl_plus  = 0


  # rucne vytvoreny seznam stanic a jejich frekvenci
  stanice = {}
  stanice[0] = [93.1  , "Radiozurnal"]
  stanice[1] = [94.1  , "Frekvence 1"]
  stanice[2] = [95    , "Blanik"]
  stanice[3] = [97.7  , "Kiss JC"]
  stanice[4] = [101.1 , "Radio Orlik"]
  stanice[5] = [103.2 , "CRo 2 - Praha"]
  stanice[6] = [105.5 , "Evropa 2"]
  stanice[7] = [106.4 , "CRo Ceske Budejovice"]

  #  v promenne "float(stanice[index][0])" je frekvence stanice s prislusnym indexem
  #  v promenne "stanice[index][1]" je jmeno stanice s prislusnym indexem  


  pocet_stanic = len(stanice)

  index = 0                      # Pri spusteni podprogramu nastav frekvenci na nultou stanici
  print stanice[index][1]      
  nastav_f(stanice[index][0])  

  # hlavni smycka na testovani dvou rozpinacich tlacitek
  while ((tl_minus == 0) or (tl_plus == 0)):  # kdyz jsou obe stlacena, nebo kdyz chybi, smycka se ukonci
    tl_minus = GPIO.input(pin_tlm)            # cteni stavu tlacitek na GPIO pinech
    tl_plus  = GPIO.input(pin_tlp)


    if (tl_plus == 1):           # pri stisku PLUS tlacitka se prepne na nasledujici stanici v seznamu
      time.sleep(0.5)
      if (tl_minus == 0):        # kdyz neni stisknuto zaroven i MINUS tlacitko...
        index = index + 1        # ... presune se index na nasledujici stanici
        if (index > (pocet_stanic-1)):  # kdyz je potom index vetsi, nez pocet stanic ...
          index = 0                     #   ... nastavi se index na zacatek seznamu
 
        print stanice[index][1]        
        nastav_f(stanice[index][0])  # nastav frekvenci aktualni stanice


    if (tl_minus == 1):          # pri stisku MINUS tlacitka se prepne na predchozi stanici v seznamu
      time.sleep(0.5)
      if (tl_plus == 0):         # kdyz neni stisknuto zaroven i PLUS tlacitko...
        index = index - 1        # ... presune se index na predchozi stanici
        if (index < 0):          # kdyz index "podleze" pod prvni stanici ...
          index = (pocet_stanic-1)  # ... nastavi se index na posledni stanici v seznamu

        print stanice[index][1]        
        nastav_f(stanice[index][0])  # nastav frekvenci aktualni stanice

    time.sleep(0.1)





# ================================================
# zacatek programu - vyhodnoceni parametru prikazove radky
# ================================================


try:                        # pokud prvni parametr chybi, zobrazi se napoveda
  parametr=sys.argv[1]
except:
  parametr=""


if (parametr=="-n"):        # prime nastaveni konkretni frekvence
  try:
    freq= float(sys.argv[2])
  except:
    freq=0
  nastav_f(freq)


elif (parametr == "-sn"):    # automaticke skenovani "NAHORU" od zadane frekvence
  try:
    freq= float(sys.argv[2])
  except:
    freq=87.5                # kdyz parametr chybi, nebo je chybny, nastavi se dolni hranice pasma
  sken(freq, True)           # sken od zadane frekvence NAHORU



elif (parametr == "-sd"):    # automaticke skenovani "DOLU" od zadane frekvence
  try:
    freq= float(sys.argv[2])
  except:
    freq=108                 # kdyz parametr chybi, nebo je chybny, nastavi se horni hranice pasma
  sken(freq, False ) # sken od zadane frekvence DOLU



elif (parametr == "-v"):     # automaticke vypis vsech silnych frekvenci
  sken(87.5, True )          # sken od zacatku pasma NAHORU



elif (parametr == "-h0"):    # ztlumit hlasitost
  bajt1 = bus.read_byte( 0x60 )
  bajt1 = bajt1 | 0b10000000 
  bus.write_byte(0x60,bajt1)



elif (parametr == "-h1"):    # obnovit hlasitost
  bajt1 = bus.read_byte( 0x60 )
  bajt1 = bajt1 & 0b01111111 
  bus.write_byte(0x60,bajt1)



elif (parametr == "-t"):     # pouziti tlacitek na GPIO k automatickemu hledani nejblizsich stanic
  tlacitka()



elif (parametr == "-p"):     # pouziti tlacitek na GPIO k prepinani predvolenych stanic
  prepinac()



else:                        # pokud prvni parametr nevyhovuje zadne variante, zobrazi se napoveda
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
  print "           when searching automatically after a station (0 to 15)"
  
