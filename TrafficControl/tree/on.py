#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT) #relay 1 white
GPIO.setup(23,GPIO.OUT) #relay 2 blue
GPIO.setup(21,GPIO.OUT) #relay 3 yellow1
GPIO.setup(25,GPIO.OUT) #relay 4 yellow2
GPIO.setup(12,GPIO.OUT) #relay 5 yellow3
GPIO.setup(16,GPIO.OUT) #relay 6 green
GPIO.setup(20,GPIO.OUT) #relay 7 red
GPIO.setup(24,GPIO.OUT) #relay 8 gate
GPIO.setup(0,GPIO,OUT) #reset button
GPIO.setup(2,GPIO,OUT) #start button

while True:
	GPIO.output(18,GPIO.HIGH)
	GPIO.output(23,GPIO.HIGH)
	GPIO.output(24,GPIO.LOW)
	GPIO.output(25,GPIO.HIGH)
	GPIO.output(12,GPIO.LOW)
	GPIO.output(16,GPIO.HIGH)
	GPIO.output(20,GPIO.LOW)
	GPIO.output(21,GPIO.HIGH)
 
