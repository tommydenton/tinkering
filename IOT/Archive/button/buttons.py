import RPi.GPIO as GPIO
import time, os, atexit, datetime, sys

haltbutton = 26

GPIO.setmode(GPIO.BCM)

GPIO.setup(haltbutton, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def Shutdown(channel):
 print(str(datetime.datetime.now()), " Shut It Down")
 os.system("sudo shutdown -h now")
 sys.stdout.flush()

def cleanup():
 GPIO.cleanup()

atexit.register(cleanup)

GPIO.add_event_detect(haltbutton, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)

# Wait indefinitely...
print str(datetime.datetime.now()), " Ready!"
sys.stdout.flush()

while True:
    time.sleep(0.1);
