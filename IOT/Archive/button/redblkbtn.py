import RPi.GPIO as GPIO
import time
import os
import sys
from pubnub import Pubnub

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(7, GPIO.OUT)

pubnub = Pubnub(publish_key='pub-c-dc523a3b-b81c-430d-9eb6-37ffa0c9053c', subscribe_key='sub-c-2e3bb45c-1f8e-11e5-9dff-0619f8945a4f')

monitor = 'iot_garage_monitor'

def reset():
     pubnub.publish(channel=monitor, message='RedBlkBtn.py GIPIO Reset Ready to Go')

reset()

def Shutdown(channel):
     pubnub.publish(channel=monitor, message='RedBlkBtn.py Requested to Shutdown')
#    os.system("sudo shutdown -h now")

def FireRelay(channel):
    GPIO.output(7,False)
    time.sleep(0.9)
    GPIO.output(7,True) 
    pubnub.publish(channel=monitor, message='RedBlkBtn.py Relay Fired')

GPIO.add_event_detect(17, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)

GPIO.add_event_detect(22, GPIO.FALLING, callback = FireRelay, bouncetime = 2000)

while 1:
 time.sleep(0.2)
