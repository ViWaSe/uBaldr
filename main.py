# Simple script to start the Device
Version = '4.1'

# start Light-Control in last known state
import LightControl

print('PicoW LightControl Version', Version)

# Connect to WLAN using PicoWifi-Module
import PicoWifi as wlan
wlan.connect()

import PicoClient as MQTT
print('>>> PicoClient is running!')
MQTT.go()