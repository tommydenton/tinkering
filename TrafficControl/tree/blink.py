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
GPIO.setwarnings(False)
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

def reset_led():
	GPIO.output(white,GPIO.LOW) 
	GPIO.output(blue,GPIO.LOW) 
	GPIO.output(topyellow,GPIO.LOW)
	GPIO.output(midyellow,GPIO.LOW)
	GPIO.output(btmyellow,GPIO.LOW)
	GPIO.output(green,GPIO.LOW)
	GPIO.output(red,GPIO.LOW)
	GPIO.output(gate,GPIO.LOW)

def start_led():
	GPIO.output(white,GPIO.HIGH) #white
	time.sleep(1) 
	GPIO.output(blue,GPIO.HIGH) #blue
	time.sleep(3) 
	GPIO.output(white,GPIO.LOW) #white
	GPIO.output(blue,GPIO.LOW) #blue
	GPIO.output(topyellow,GPIO.HIGH) #yellow1
	time.sleep(.1)
	GPIO.output(midyellow,GPIO.HIGH) #yellow2
	time.sleep(.1)
	GPIO.output(btmyellow,GPIO.HIGH) #yellow3
	time.sleep(.2)
	GPIO.output(green,GPIO.HIGH) #green
	GPIO.output(btmyellow,GPIO.LOW) #yellow1
	GPIO.output(midyellow,GPIO.LOW) #yellow2
	GPIO.output(topyellow,GPIO.LOW) #yellow3
	time.sleep(5) 
	GPIO.output(green,GPIO.LOW) #green
	time.sleep(3)
	while True:
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(1) 
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(topyellow,GPIO.HIGH) #yellow1
		GPIO.output(midyellow,GPIO.HIGH) #yellow2
		GPIO.output(btmyellow,GPIO.HIGH) #yellow3
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(btmyellow,GPIO.LOW) #yellow1
		GPIO.output(midyellow,GPIO.LOW) #yellow2
		GPIO.output(topyellow,GPIO.LOW) #yellow3
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(1) 
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.HIGH) #red
		GPIO.output(green,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(red,GPIO.LOW) #red
		GPIO.output(green,GPIO.LOW) #green
		time.sleep(1)

try:
	while True:
		prev_input = 0
		input_state = GPIO.input(resetbtn)
		if ((not prev_input ) and input_state):
			print('Reset Button Pressed')
			reset_led()
			time.sleep(0.2)
		prev_input = input     

		input_state = GPIO.input(startbtn)
		if ((not prev_input ) and input_state):
			print('Start Button Pressed')
			start_led()
			time.sleep(0.2)
		prev_input = input

except:
		GPIO.cleanup() 