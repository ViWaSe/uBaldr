# Simple script to start the Device
Version = '5.3.2'

# add subdirectories to path
import sys
sys.path.insert(0, "./modules")
sys.path.insert(0, "./params")

# start Light-Control
import LightControl

print('[ INFO ] Welcome to BALDR Version', Version)

# Connect to WLAN using PicoWifi-Module
import PicoWifi as wlan
wlan.connect()
print('[ INFO ] PicoWifi is connected!')

# Establish MQTT-Connection 
import PicoClient as MQTT
print('[ INFO ] PicoClient is running!')
MQTT.go()