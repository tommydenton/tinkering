#!/usr/bin/python

#bmp280
import Adafruit_BMP.BMP280 as BMP280
sensor = BMP280.BMP280()
tempBMP = sensor.read_temperature()
pressureBMP = sensor.read_pressure()
altitudeBMP = sensor.read_altitude()
sealevelBMP = sensor.read_sealevel_pressure()
sealevel = 1010.3

#AM2303
import Adafruit_DHT
sensor = Adafruit_DHT.AM2302
pin = 17
humidityDHT, tempDHT = Adafruit_DHT.read_retry(sensor, pin)

#Calcs
import time
from datetime import datetime
from time import strftime, localtime
from meteocalc import dew_point, heat_index
tBMP = tempBMP*9/5+32
tDHT = tempDHT*9/5+32
hDHT = humidityDHT
dpBMPc = dew_point(temperature=tempBMP, humidity=hDHT)
hiBMPc = heat_index(temperature=tempBMP, humidity=hDHT)
dpDHTc = dew_point(temperature=tempDHT, humidity=hDHT)
hiDHTc = heat_index(temperature=tempDHT, humidity=hDHT)
dpBMP = dpBMPc*9/5+32
dpDHT = dpDHTc*9/5+32
hiBMP = hiBMPc*9/5+32
hiDHT = hiDHTc*9/5+32

pBMP = pressureBMP*0.00029529980164712
hpBMP = pressureBMP/100

calti = (44330.0 * (1.0 - pow(pressureBMP / (sealevel*100), 1.0/5.255)))
caltitude = calti*3.28084
maltitude = altitudeBMP*3.28084

#format to write
import os
import csv,sys
BMP208Temp = format(tBMP, '0.2f')
DHTTemp = format(tDHT, '0.2f')
DHTHumidity = format(hDHT, '0.2f')
BMPPressure = format(pBMP, '0.2f')

#time
start_time = time.time()
datetime = strftime("%H:%M:%S %m/%d/%y")

#output
print ''
print ''
print 'dateTime,', datetime
print ''
print 'TempBMP = {0:0.2f} *F'.format(tBMP)
print 'TempDHT = {0:0.2f} *F'.format(tDHT)
print 'TempBMP = {0:0.2f} *c'.format(tempBMP)
print 'TempDHT = {0:0.2f} *c'.format(tempDHT)
print ''
print 'HumidityDHT = {0:0.2f} %'.format(hDHT)
print ''
print 'Dew Point BMP = {0:0.2f} *F'.format(dpBMP.f)
print 'Dew Point DHT = {0:0.2f} *F'.format(dpDHT.f)
print 'Feels Like BMP = {0:0.2f} *F'.format(hiBMP.f)
print 'Feels like DHT = {0:0.2f} *F'.format(hiDHT.f)
print ''
print 'Pressure = {0:0.2f} in Hg'.format(pBMP)
print 'Pressure = {0:0.2f} Pa'.format(pressureBMP)
print 'cAltitude = {0:0.2f} feet'.format(caltitude)
print 'mAltitude = {0:0.2f} feet'.format(maltitude)
print ''
print ''
print ''

# writeout measurements
#f = open('measurements.csv', 'wt')
#writer = csv.writer(f)
#writer.writerow( ('Measurement', 'Reading') )
#writer.writerow( ('Temperature in degrees F', t ) )
#writer.writerow( ('Barometric Pressure in in of Hg', b ) )
#writer.writerow( ('Humidity in Percent', h ) )
#writer.writerow( ('Dew Point in in degrees F', d ) )
#if temp <= 80.00:
# writer.writerow( ('Feels like', t ) )
#else:
# writer.writerow( ('Feels like in Degrees F', hi ) )
#writer.writerow( ('Time and data of reading', datetime ) )
#f.close()

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


#print 'Sealevel Pressure = {0:0.2f} Pa'.format(sealevelBMP)

#if tBMP <= 80.00:
# print 'No Heat Index needed,','00.000'
#else:
# print 'Heat Index BMP = {0:0.2f} *F'.format(dpBMPc.f)
#
#if tDHT <= 80.00:
# print ''
#else:
# print 'Heat Index DHT = {0:0.2f} *F'.format(dpDHTc.f)


#dpBMPc = dew_point(temperature=tempBMP, humidity=hDHT)
#hiBMPc = heat_index(temperature=tempBMP, humidity=hDHT)
#dpDHTc = dew_point(temperature=tempDHT, humidity=hDHT)
#hiDHTc = heat_index(temperature=tempDHT, humidity=hDHT)
