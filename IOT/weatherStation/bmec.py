#!/usr/bin/python

#bmp280
import Adafruit_BMP.BMP280 as BMP280
sensor = BMP280.BMP280()

#AM2303
import Adafruit_DHT
sensor = Adafruit_DHT.AM2302
pin = 17
humidity, temp = Adafruit_DHT.read_retry(sensor, pin)

#Calcs
import time
from datetime import datetime
from time import strftime, localtime
from meteocalc import dew_point, heat_index
tempf = temp*9/5+32
#temp = degrees*9/5+32
#hectopascals = pascals / 100
#baro = 0.02952998751*hectopascals
dewpoint = dew_point(temperature=tempf, humidity=humidity)
#dewpoint = dew_point(temperature=degrees, humidity=humidity)
heatindex = heat_index(temperature=tempf, humidity=humidity)
#heatindex = heat_index(temperature=degrees, humidity=humidity)

#format to print
import os
import csv,sys
t = format(temp, '0.2f')
#b = format(baro, '0.2f')
h = format(humidity, '0.2f')
d = format(dewpoint.f, '0.2f')
hi = format(heatindex.f, '0.2f')

#time
start_time = time.time()
datetime = strftime("%H:%M:%S %m/%d/%y")

print 'dateTime,', datetime
print 'Temp,',format(tempf, '0.2f')
#print 'Baro,',format(baro, '0.2f')
print 'Humi,',format(humidity, '0.2f')
print 'DewP,',format(dewpoint.f, '0.2f')
if temp <= 80.00:
 print 'Heat,','00.000'
else:
 print 'Heat,',format(heatindex.f, '0.2f')
print 'Temp = {0:0.2f} *C'.format(sensor.read_temperature())
print 'Pressure = {0:0.2f} Pa'.format(sensor.read_pressure())
print 'Altitude = {0:0.2f} m'.format(sensor.read_altitude())
print 'Sealevel Pressure = {0:0.2f} Pa'.format(sensor.read_sealevel_pressure())

# writeout measurements
f = open('measurements.csv', 'wt')
writer = csv.writer(f)
writer.writerow( ('Measurement', 'Reading') )
writer.writerow( ('Temperature in degrees F', t ) )
#writer.writerow( ('Barometric Pressure in in of Hg', b ) )
writer.writerow( ('Humidity in Percent', h ) )
writer.writerow( ('Dew Point in in degrees F', d ) )
if temp <= 80.00:
 writer.writerow( ('Feels like', t ) )
else:
 writer.writerow( ('Feels like in Degrees F', hi ) )
writer.writerow( ('Time and data of reading', datetime ) )
f.close()

# weewx data
#f = open('/var/www/html/weather/wxdata.csv', 'wt')
#writer = csv.writer(f)
#writer.writerow( ('dateTime', 'barometer', 'outTemp', 'outHumidity') )
#writer.writerow( (datetime, b, t, h ) )
#f.close()

from picamera import PiCamera
from time import sleep

camera = PiCamera()

camera.rotation = 90
camera.resolution = (640, 480)
camera.framerate = 30

camera.start_preview()
camera.brightness = 70
camera.contrast = 70
camera.annotate_text = "Callender Dr., FTW, Texas"

camera.capture('max.jpg')

#video
#camera.start_preview()
#camera.start_recording('/home/pi/video.h264')
#sleep(10)
#camera.stop_recording()
#camera.stop_preview()

# move files into place
#os.system("sudo rsync -avz /media/usb/weather/ -e 'ssh -p 8997 -i /home/pi/.ssh/id_rsa' pi@iot.tommydenton.com:/home/pi/weather")
#os.system("sudo cp /media/usb/weather/measurements.csv /var/www/html/weather/measurements.csv")
#os.system("sudo cp /media/usb/weather/max.jpg /var/www/html/weather/max.jpg")
#from shutil import copyfile



#old bme
#from Adafruit_BME280 import *
#sensor = BME280(mode=BME280_OSAMPLE_8)
#degrees = sensor.read_temperature()
#pascals = sensor.read_pressure()
