import RPi.GPIO as GPIO
import time
import sys
import os
from pubnub import Pubnub

GPIO.setmode (GPIO.BCM)
SENSORPIN = 18
sensorTrigger = True

theChannel = 'iot_garage_sensor'
monitor = 'iot_garage_monitor'

GPIO.setup(SENSORPIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)

pubnub = Pubnub(publish_key='pub-c-dc523a3b-b81c-430d-9eb6-37ffa0c9053c', subscribe_key='sub-c-2e3bb45c-1f8e-11e5-9dff-0619f8945a4f')

pubnub.publish(channel=monitor, message='Sensor.py is ready')

while True:
        time.sleep(0.2)
	if GPIO.input(SENSORPIN):
		if (sensorTrigger):
                        pubnub.publish(channel=theChannel, message='Opened')
                        pubnub.publish(channel=monitor, message='Sensor was Opened')
			sensorTrigger = False
	if not GPIO.input(SENSORPIN):
		if not (sensorTrigger):
                        pubnub.publish(channel=theChannel, message='Closed')
                        pubnub.publish(channel=monitor, message='Sensor was Closed')
			sensorTrigger = True
