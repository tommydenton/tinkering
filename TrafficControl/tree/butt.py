#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT) #yellow1
GPIO.setup(22,GPIO.OUT) #yellow2
GPIO.setup(23,GPIO.OUT) #yellow3
GPIO.setup(24,GPIO.OUT) #green
GPIO.setup(25,GPIO.OUT) #Blue
GPIO.setup(27,GPIO.OUT) #red
GPIO.setup(21,GPIO.IN) #Button

while True:

    # Turn LED off
    print ("LED off")
    GPIO.output(27, GPIO.LOW)
    
    # waiting for button press
    while GPIO.input(21) == 1:
        time.sleep(0.2) 
        
    # Turn LED on
    print ("LED on")
    GPIO.output(27, GPIO.HIGH)


    # waiting for button release
    while GPIO.input(21) == 0:
        time.sleep(0.2)         
