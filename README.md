

<img width="1024" height="1024" alt="BaldrOS" src="https://github.com/user-attachments/assets/14234b7b-3ecf-4e38-92b5-b50994df123f" />

# uBaldr
This is a Micropython Smarthome / IoT-project using Raspberry PicoW or ESP-32 microcontroller.

# Purpose
You can use this project to control Neopixel-LEDs via the MQTT-Protocoll. A MQTT-Broker is needed to run the project and can i.E. be realized by a Raspberry Pi.
JSON-Strings are used for communication. Please see documentation pdf for more info!

# Features
- Set Color by line-animation (pixel by pixel) with defined speed. Supported formats: hex, [r,g,b] and [r,g,b,w]
- Set Color by smooth animantion (all pixel at same time). Parametere are the same as by line-animation
- Dim LEDs with defined speed
- OTA-Updates
- Change settings via MQTT-Message
- Log-function
- NTP

# Supported Hardware
- uBaldr fully supports Raspberry PicoW and ESP32-S3 Microcontrollers. Note that you need to change the onboard-led-settings depending on your device.
- NeoPixel-LEDs are supported in RGB, RGBW and WW/CW Variants

# Usage
The Project works with MQTT-Topics. <client>/order ist the order you send to the client. Messages from the client are published to <client>/status.
  - Example 1 - Set the color of your LED-Strip to rgb-red (255,0,0) by line-animation. You can set a speed (pause between pixels in ms).
    - JSON-String to <client>/order:
    > {"sub_type": "LC", "command": "line", "payload": [255,0,0], "speed": 5}
    - Answer from device/status: True
  - Example 2 - dim the light to 5% with 1ms between %-steps
    - JSON-String to <client>/order:
    > {"sub_type": "LC", "command": "dim", "payload": 5, "speed": 1}
    - Answer from device/status: True
  - You can also just send a command without parameters like speed. In this case dafault values are used.
  - There is also an /log-topic to get logfiles (device/status/log)

# MQTT topics
The Topics are created from the client-name that is set in the config.json (MQTT-Config -> Client).
  - <client>/order: Used for commands to control thie client
  - <client>/status: Status messages from the client
  -   <client>/status/log: Used to return logs
  -   <client>/status/update: Used for OTA-Update status, like progress

# Micropython-Files
You find everything you need to copy to your µPython-device in the uBaldr-Folder.
Change the config.json and fill in your wifi-settings and MQTT-settings before start!

# The coonfig.json file
Configuration is stored in a JSON file, named config.json that is explained in that section. 
## Wifi-config
country:       Network country (only used for RPI)
IP:            IP-Adress, can be empty, is created from uWifi.py
PW:            Your Wifi-Password
SSID:          Your Wifi-SSID
Hostname:      Set a Hostname
onboard_led:   Onboard-LED-Pin (default=21)
led_inverted:  True, if you use a ESP-32-S3
led_active:    Can be false if you don't want to use the status-LED

## MQTT-config:
Broker:            The Broker's IP-Adress
Client:            Set a unique client name for each device -> Topics are created from that name
md_pin:            Pin for sensor (currently not used)
Port:              The MQTT Network-Port (1883 by default)
PW:                MQTT Password, if needed
User:              MQTT User, if needed
publish_in_json:   Publish Messages in json-format? (true by default)

## LightControl_settings
autostart:        Set the LEDs to the last saved state when power on (true by default)
bytes_per_pixel:  Set Bytes per pixel (i.e. 3 for RGB, 4 for RGBW, ...)
led_pin:          LEDs Data-Pin
led_qty:          Quantity of the used LEDs

## Options
This section is currently not used

# OTA-Update
To trigger an OTA-Update, send this JSON-String to the device/order Topic:
>{
    "sub_type": "admin",
    "command": "get_update",
    "module": "all",
    "base_url": "https://raw.githubusercontent.com/ViWaSe/uBaldr/refs/heads/main/uBaldr/"
}
Note that the OTA-Update function is still under developement.
