#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT) #relay 1
GPIO.setup(23,GPIO.OUT) #relay 2
GPIO.setup(24,GPIO.OUT) #relay 3 Dead
GPIO.setup(25,GPIO.OUT) #relay 4
GPIO.setup(12,GPIO.OUT) #relay 5 Dead
GPIO.setup(16,GPIO.OUT) #relay 6
GPIO.setup(20,GPIO.OUT) #relay 7 Dead
GPIO.setup(21,GPIO.OUT) #relay 8

while True:
	GPIO.output(18,GPIO.HIGH)
	GPIO.output(23,GPIO.HIGH)
	GPIO.output(24,GPIO.LOW)
	GPIO.output(25,GPIO.HIGH)
	GPIO.output(12,GPIO.LOW)
	GPIO.output(16,GPIO.HIGH)
	GPIO.output(20,GPIO.LOW)
	GPIO.output(21,GPIO.HIGH)
 
