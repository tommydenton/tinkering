#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12,GPIO.OUT) #blue
GPIO.setup(16,GPIO.OUT) #yellow1
GPIO.setup(18,GPIO.OUT) #yellow2
GPIO.setup(20,GPIO.OUT) #yellow3
GPIO.setup(21,GPIO.OUT) #green
GPIO.setup(23,GPIO.OUT) #red
GPIO.setup(24,GPIO.OUT) #open
GPIO.setup(25,GPIO.OUT) #open

while True:
		GPIO.output(12,GPIO.LOW) 
		GPIO.output(16,GPIO.LOW) 
		GPIO.output(18,GPIO.LOW)
		GPIO.output(20,GPIO.LOW)
		GPIO.output(21,GPIO.LOW)
		GPIO.output(23,GPIO.LOW)
		GPIO.output(24,GPIO.LOW)
		GPIO.output(25,GPIO.LOW)
		time.sleep(.5) 
		GPIO.output(12,GPIO.HIGH) #blue
		time.sleep(3) 
		GPIO.output(12,GPIO.LOW) #blue
		GPIO.output(16,GPIO.HIGH) #yellow1
		time.sleep(.5)
		GPIO.output(18,GPIO.HIGH) #yellow2
		time.sleep(.5)
		GPIO.output(20,GPIO.HIGH) #yellow3
		time.sleep(.1)
		GPIO.output(16,GPIO.LOW) #yellow1
		GPIO.output(18,GPIO.LOW) #yellow2
		GPIO.output(20,GPIO.LOW) #yellow3
		GPIO.output(21,GPIO.HIGH) #green
		time.sleep(3) 
		GPIO.output(21,GPIO.LOW)
		time.sleep(3) 
		GPIO.output(23,GPIO.HIGH)
		time.sleep(3) 
