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
	if (GPIO.input(21)):
		print("on")
		GPIO.output(27, GPIO.HIGH)
while False:
	if (GPIO.input(13)):  
		GPIO.output(17,GPIO.LOW) 
		GPIO.output(22,GPIO.LOW)
		GPIO.output(23,GPIO.LOW)
		GPIO.output(24,GPIO.LOW)
		GPIO.output(25,GPIO.LOW)
		GPIO.output(27,GPIO.LOW)
		time.sleep(.5) 
		GPIO.output(25,GPIO.HIGH) #blue
		time.sleep(3) 
		GPIO.output(25,GPIO.LOW) #blue
		GPIO.output(17,GPIO.HIGH) #yellow1
		time.sleep(.5)
		GPIO.output(22,GPIO.HIGH) #yellow2
		time.sleep(.5)
		GPIO.output(23,GPIO.HIGH) #yellow3
		time.sleep(.1)
		GPIO.output(17,GPIO.LOW) #yellow1
		GPIO.output(22,GPIO.LOW) #yellow2
		GPIO.output(23,GPIO.LOW) #yellow3
		GPIO.output(24,GPIO.HIGH) #green
		time.sleep(3) 
		GPIO.output(24,GPIO.LOW)
		time.sleep(3) 
		GPIO.output(27,GPIO.HIGH)
		time.sleep(3) 
		GPIO.output(27,GPIO.LOW)
