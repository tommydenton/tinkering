#!/usr/bin/python

from gpiozero import Button
from signal import pause
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
GPIO.setup(0,GPIO.OUT) #reset button
GPIO.setup(2,GPIO.OUT) #start button

def say_hello_reset():
	while True:
		GPIO.output(18,GPIO.LOW) 
		GPIO.output(23,GPIO.LOW) 
		GPIO.output(21,GPIO.LOW)
		GPIO.output(25,GPIO.LOW)
		GPIO.output(12,GPIO.LOW)
		GPIO.output(16,GPIO.LOW)
		GPIO.output(20,GPIO.LOW)
		GPIO.output(24,GPIO.LOW)

def say_goodbye_reset():
	while True:
		GPIO.output(18,GPIO.HIGH) #white
		time.sleep(1) 
		GPIO.output(23,GPIO.HIGH) #blue
		time.sleep(3) 
		GPIO.output(18,GPIO.LOW) #white
		GPIO.output(23,GPIO.LOW) #blue
		GPIO.output(21,GPIO.HIGH) #yellow1
		time.sleep(.1)
		GPIO.output(25,GPIO.HIGH) #yellow2
		time.sleep(.1)
		GPIO.output(12,GPIO.HIGH) #yellow3
		time.sleep(.2)
		GPIO.output(16,GPIO.HIGH) #green
		GPIO.output(12,GPIO.LOW) #yellow1
		GPIO.output(25,GPIO.LOW) #yellow2
		GPIO.output(21,GPIO.LOW) #yellow3
		time.sleep(5) 
		GPIO.output(16,GPIO.LOW) #green
		time.sleep(3) 
		GPIO.output(20,GPIO.HIGH) #red
		GPIO.output(16,GPIO.HIGH) #green
		time.sleep(1) 
		GPIO.output(20,GPIO.LOW) #red
		GPIO.output(16,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(20,GPIO.HIGH) #red
		GPIO.output(16,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(20,GPIO.LOW) #red
		GPIO.output(16,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(20,GPIO.HIGH) #red
		GPIO.output(16,GPIO.HIGH) #green
		time.sleep(.5)
		GPIO.output(20,GPIO.LOW) #red
		GPIO.output(16,GPIO.LOW) #green
		time.sleep(.5)
		GPIO.output(20,GPIO.HIGH) #red
		GPIO.output(16,GPIO.HIGH) #green
		time.sleep(.5)

	def say_hello_start():
		print("Hello! start")

	def say_goodbye_start():
		print("Goodbye! start")

	button = Button(0)

	button.when_pressed = say_hello_reset
	button.when_released = say_goodbye_reset

	button = Button(2)

	button.when_pressed = say_hello_start
	button.when_released = say_goodbye_start


	pause()