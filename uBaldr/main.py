# Simple script to start uBaldr
version = [7,0,0]

from uWifi import Client
import PicoClient as MQTT
import LightControl

# start Light-Control
print('[ INFO ] Welcome to BALDR Version', version)

# Connect to WLAN using PicoWifi-Module
wlan = Client()
wlan.connect()
print('[ INFO ] PicoWifi is connected!')

# Establish MQTT-Connection 
print('[ INFO ] PicoClient is running!')
MQTT.go()