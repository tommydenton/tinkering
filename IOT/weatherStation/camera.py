from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 90
camera.resolution = (2592, 1944)
camera.framerate = 30

camera.start_preview()
#camera.start_preview(alpha=100)
camera.brightness = 70
camera.contrast = 70
#camera.exposure_mode = 'night'
#camera.awb_mode = 'sunlight'
camera.annotate_text = "TGUNN WeatherPi!"

camera.capture('max.jpg')

#for i in range(5):
#    sleep(2)
#    camera.capture('/media/usb/weather/image%s.jpg' % i)
#camera.stop_preview()


#video
#camera.start_preview()
#camera.start_recording('/home/pi/video.h264')
#sleep(10)
#camera.stop_recording()
#camera.stop_preview()

import os, sys
os.system("sudo rsync -avz max.jpg -e 'ssh -p 8997 -i /home/pi/.ssh/id_rsa' pi@iot.tommydenton.com:/home/pi/weather")
