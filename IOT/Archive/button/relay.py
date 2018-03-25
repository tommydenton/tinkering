import RPi.GPIO as GPIO
import time
import sys
from pubnub import Pubnub

RELAYPIN = 7

GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RELAYPIN, GPIO.OUT)

pubnub = Pubnub(publish_key='pub-c-dc523a3b-b81c-430d-9eb6-37ffa0c9053c', subscribe_key='sub-c-2e3bb45c-1f8e-11e5-9dff-0619f8945a4f')

theChannel = 'iot_garage_door'
monitor = 'iot_garage_monitor'

def _reset():
        pubnub.publish(channel=monitor, message='Relay.py Reset Redayd to Work')

_reset()

def _error():
	print(channel)
        pubnub.publish(channel=monitor, message=channel)

def _callback(m, channel):
	if m['RELAY'] == 1:
		for i in range(1):
		    GPIO.output(RELAYPIN,False)
		    time.sleep(0.9) 
                    GPIO.output(RELAYPIN,True)
                    pubnub.publish(channel=monitor, message='Relay.py Fired')
        else:
                    pubnub.publish(channel=monitor, message='Relay.py Quit')
		    quit()

pubnub.subscribe(channels=theChannel, callback=_callback, error=_error)
