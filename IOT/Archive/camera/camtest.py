from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 270
camera.resolution = (2592, 1944)
#camera.framerate = 15


camera.start_preview()
#camera.start_preview(alpha=200)
#camera.brightness = 70
#camera.contrast = 70
camera.exposure_mode = 'night'
#camera.awb_mode = 'sunlight'
#camera.annotate_text = "Hello world!"

#camera.capture('/home/pi/Desktop/max.jpg')

for i in range(5):
    sleep(2)
    camera.capture('/media/usb/weather/image%s.jpg' % i)
camera.stop_preview()


#video
#camera.start_preview()
#camera.start_recording('/home/pi/video.h264')
#sleep(10)
#camera.stop_recording()
#camera.stop_preview()


