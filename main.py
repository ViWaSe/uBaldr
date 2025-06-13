# Simple script to start the Device
Version = '5.1.1'

import sys
sys.path.insert(0, "./modules")

# start Light-Control
import LightControl

print('PicoW LightControl Version', Version)

# Connect to WLAN using PicoWifi-Module
import PicoWifi as wlan
wlan.connect()

# Establish MQTT-Connection 
import PicoClient as MQTT
print('>>> PicoClient is running!')
MQTT.go()