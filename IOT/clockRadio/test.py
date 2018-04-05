# coding=utf-8
 
import RPi.GPIO as GPIO
import datetime
  
def my_callback0(channel):
  if GPIO.input(26) == GPIO.LOW:
    print('\n▼  at ' + str(datetime.datetime.now()))
  else:
    print('\n ▲ at ' + str(datetime.datetime.now())) 

def my_callback1(channel):
  if GPIO.input(20) == GPIO.LOW:
    print('\n▼  at 20' )
  else:
    print('\n ▲ at 20' ) 

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(26, GPIO.BOTH, callback=my_callback0)
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(20, GPIO.BOTH, callback=my_callback1)
    
    message = raw_input('\nPress any key to exit.\n')

finally:
    GPIO.cleanup()

print("Goodbye!")
