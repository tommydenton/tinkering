#!/usr/bin/python

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT) #relay 1
GPIO.setup(23,GPIO.OUT) #relay 2
GPIO.setup(24,GPIO.OUT) #relay 3
GPIO.setup(25,GPIO.OUT) #relay 4
GPIO.setup(12,GPIO.OUT) #relay 5
GPIO.setup(16,GPIO.OUT) #relay 6
GPIO.setup(20,GPIO.OUT) #relay 7
GPIO.setup(21,GPIO.OUT) #relay 8

while True:
		GPIO.output(18,GPIO.LOW) 
		GPIO.output(23,GPIO.LOW) 
		GPIO.output(24,GPIO.LOW)
		GPIO.output(25,GPIO.LOW)
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.LOW)
		GPIO.output(20,GPIO.LOW)
		GPIO.output(21,GPIO.LOW)
		GPIO.output(12,GPIO.HIGH) #white
		time.sleep(.5) 
		GPIO.output(12,GPIO.HIGH) #blue
		time.sleep(3) 
		GPIO.output(12,GPIO.LOW) #blue
		GPIO.output(16,GPIO.HIGH) #yellow1
		time.sleep(.1)
		GPIO.output(18,GPIO.HIGH) #yellow2
		time.sleep(.1)
		GPIO.output(20,GPIO.HIGH) #yellow3
		time.sleep(.2)
		GPIO.output(21,GPIO.HIGH) #green
		GPIO.output(16,GPIO.LOW) #yellow1
		GPIO.output(18,GPIO.LOW) #yellow2
		GPIO.output(20,GPIO.LOW) #yellow3
		time.sleep(5) 
		GPIO.output(21,GPIO.LOW) #green
		time.sleep(3) 
		GPIO.output(23,GPIO.HIGH) #red
		GPIO.output(21,GPIO.HIGH) #green
		time.sleep(1) 
		GPIO.output(23,GPIO.LOW) #red
		GPIO.output(21,GPIO.LOW) #green
		time.sleep(.1)
		GPIO.output(23,GPIO.HIGH) #red
		GPIO.output(21,GPIO.HIGH) #green
		time.sleep(2)