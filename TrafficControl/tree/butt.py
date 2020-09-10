#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import gc

gc.collect()

white = 18
blue = 23
topyellow = 21
midyellow = 25
btmyellow = 12
green = 16
red = 20
gate = 24
resetbtn = 5
startbtn = 6

GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(white,GPIO.OUT) #relay 1 white
GPIO.setup(blue,GPIO.OUT) #relay 2 blue
GPIO.setup(topyellow,GPIO.OUT) #relay 3 yellow1
GPIO.setup(midyellow,GPIO.OUT) #relay 4 yellow2
GPIO.setup(btmyellow,GPIO.OUT) #relay 5 yellow3
GPIO.setup(green,GPIO.OUT) #relay 6 green
GPIO.setup(red,GPIO.OUT) #relay 7 red
GPIO.setup(gate,GPIO.OUT) #relay 8 gate
GPIO.setup(resetbtn,GPIO.IN,pull_up_down=GPIO.PUD_UP) #reset button
GPIO.setup(startbtn,GPIO.IN,pull_up_down=GPIO.PUD_UP) #start button

try:
    while True:
        input_state = GPIO.input(resetbtn)
        if input_state == False:
            print('Reset Button Pressed')
            time.sleep(0.2)
        else:
            print('reset else')

        input_state = GPIO.input(startbtn)
        if input_state == False:
            print('Start Button Pressed')
            time.sleep(0.2)
        else:
            print('start else')
except:
    GPIO.cleanup()
