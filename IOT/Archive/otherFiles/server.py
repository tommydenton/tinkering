import sys
import os
from pubnub import Pubnub

pubnub = Pubnub(publish_key='pub-c-dc523a3b-b81c-430d-9eb6-37ffa0c9053c', subscribe_key='sub-c-2e3bb45c-1f8e-11e5-9dff-0619f8945a4f')

CHANNEL = "iotgaragesensor"

def callback(message, channel):
    print "Channel %s: (%s)" % (channel, message)

print "Listening on Channel %s" % CHANNEL
pubnub.subscribe(CHANNEL, callback)
