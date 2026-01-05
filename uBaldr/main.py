# Simple script to start uBaldr
version = [7,1,2]

from uWifi import Client
import mqtt_Client as MQTT
import LightControl

# start Light-Control
print('[ INFO ] Welcome to BALDR Version', version)

# Establish MQTT-Connection 
print('[ INFO ] PicoClient is running!')
MQTT.go()