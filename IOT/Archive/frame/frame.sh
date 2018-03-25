#!/bin/bash
sleep 15
export HOME=/home/pi
cd /home/pi
DISPLAY=:0.0 XAUTHORITY=/home/pi/.Xauthority /usr/bin/feh -q -p -r -Z -F -R 60 -Y -D 15.0 /media/photos/
