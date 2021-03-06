#!/usr/bin/python

import RPi.GPIO as GPIO
import time

white = 18
blue = 23
topyellow = 24
midyellow = 25
btmyellow = 12
green = 16
red = 20
gate = 21
resetbtn = 6
startbtn = 5

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
	GPIO.output(red,GPIO.HIGH) #red
	time.sleep(1)
	GPIO.output(red,GPIO.LOW) #red
	GPIO.output(white,GPIO.HIGH) #white
	time.sleep(1) 
	GPIO.output(blue,GPIO.HIGH) #blue
	time.sleep(1.5) 
	GPIO.output(white,GPIO.LOW) #white
	GPIO.output(blue,GPIO.LOW) #blue
	time.sleep(.1) 
	GPIO.output(topyellow,GPIO.HIGH) #yellow1
	time.sleep(.1)
	GPIO.output(midyellow,GPIO.HIGH) #yellow2
	time.sleep(.1)
	GPIO.output(btmyellow,GPIO.HIGH) #yellow3
	time.sleep(.1)
	GPIO.output(green,GPIO.HIGH) #green
	GPIO.output(btmyellow,GPIO.LOW) #yellow1
	GPIO.output(midyellow,GPIO.LOW) #yellow2
	GPIO.output(topyellow,GPIO.LOW) #yellow3
	time.sleep(5) 
	GPIO.output(green,GPIO.LOW) #green
	time.sleep(3)


while True:
	input_state = GPIO.input(resetbtn)
	input_stateb = GPIO.input(startbtn)
	if input_state == False:
		print('Reset Button Pressed')
		reset_led()
		time.sleep(0.3)
	else:
		if input_stateb == False:
			print('Start Button Pressed')
			start_led()
			time.sleep(0.3)
