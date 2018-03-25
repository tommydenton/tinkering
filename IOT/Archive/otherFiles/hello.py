import sys
from pubnub import Pubnub

pubnub = Pubnub(publish_key='pub-c-dc523a3b-b81c-430d-9eb6-37ffa0c9053c', subscribe_key='sub-c-2e3bb45c-1f8e-11e5-9dff-0619f8945a4f')

channel = 'iot_garage_sensor'
data = { 'username': 'your name here',
         'message': 'Hello world from Pi!'}

def callback(m):
   print(m)

pubnub.publish(channel, data, callback=callback, error=callback)
