#!/bin/bash
if ! [ "$(ping -c 1 192.168.1.254)" ]; then
    sudo ifdown wlan0
    sudo ifup wlan0
fi
