import RPi.GPIO as GPIO
import time, os, atexit, datetime, sys

haltbutton = 13
garagebutton = 12
leds = 23
garage = 24
lightbutton = 25
BS1=False
BS2=False

GPIO.setmode(GPIO.BCM)

GPIO.setup(haltbutton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(garagebutton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(garage, GPIO.OUT)
GPIO.setup(leds, GPIO.OUT)
GPIO.setup(lightbutton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(garage, True)
GPIO.output(leds, True)

def Shutdown(channel):
 print(str(datetime.datetime.now()), " Shut It Down")
 os.system("sudo shutdown -h now")
 sys.stdout.flush()

def Button1(channel):
 print(str(datetime.datetime.now()), " Door Moving") 
 GPIO.output(garage, False)
 time.sleep(0.1)
 GPIO.output(garage, True)
 sys.stdout.flush()

def Button2(channel):
 global BS1
 print(str(datetime.datetime.now()), " Lights") 
 if BS1==False:
  GPIO.output(leds, False)
  BS1=True
  time.sleep(0.5)
 else:
  GPIO.output(leds, True)
  time.sleep(0.5)
  BS1=False
  sys.stdout.flush()

def cleanup():
 GPIO.cleanup()

atexit.register(cleanup)

GPIO.add_event_detect(haltbutton, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)
GPIO.add_event_detect(garagebutton, GPIO.FALLING, callback = Button1, bouncetime = 2000)
GPIO.add_event_detect(lightbutton, GPIO.FALLING, callback = Button2, bouncetime = 2000)

# Wait indefinitely...
print str(datetime.datetime.now()), " Ready!"
sys.stdout.flush()

while True:
    time.sleep(0.1);
