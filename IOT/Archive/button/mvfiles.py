sudo rsync -avz /media/usb/weather/ -e "ssh -p 8997 -i /home/pi/.ssh/id_rsa" pi@iot.tommydenton.com:/home/pi/weather
