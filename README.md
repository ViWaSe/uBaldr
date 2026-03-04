

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
### Topics can be set in the confic JSON-File in the section "MQTT-config". "topics" should be a list with the topics to subscribe.
### The client subscribes to 3 topics by default:
-  <b>uBaldr/all</b>			 Every device subscribes to this topic
-  <b>uBaldr/<Client-id>/main:</b> The main topic for the client
-  <b>uBaldr/<Client-id>/echo:</b> Used only for echo-messages
### There are 3 topics, the client publishes:
-  <b>uBaldr/<Client-id>/status:</b> Status-topic, used for alive-messages
-  <b>uBaldr/<Client-id>/status/log:</b> For sending logfile-content
-  <b>uBaldr/<Client-id>/answer:</b> Used for any answer-message

# Alive-JSON
- From Version 7.3, the clients sends a Alive-JSON on first connect or a message is received on uBaldr/<client-id>/echo.
- The JSON contains informations, like uptime, IP-Adress, Client-id and subscribed topics.
- Example JSON:
>{
>"status": "online",
>"uptime": "01d 04h 25m",
>"ip": "92.168.178.44",
>"mqtt_handler_version": [2,3,1],
>"client_id": "bookworm",
>"subscribed_to": [
>"uBaldr/all", 
>"uBaldr/bookworm/main",
>"uBaldr/home"
>]
>}


# Micropython-Files
You find everything you need to copy to your µPython-device in the uBaldr-Folder.
Change the config.json and fill in your wifi-settings and MQTT-settings before start!

# The coonfig.json file
Configuration is stored in a JSON file, named config.json that is explained in that section. 
## Wifi-config
- country:   </b>    Network country (only used for RPI)
- <b>IP:     </b>       IP-Adress, can be empty, is created from uWifi.py
- <b>PW:      </b>      Your Wifi-Password
- <b>SSID:      </b>    Your Wifi-SSID
- <b>Hostname:   </b>   Set a Hostname
- <b>onboard_led: </b>  Onboard-LED-Pin (default=21)
- <b>led_inverted: </b> True, if you use a ESP-32-S3
- <b>led_active:  </b>  Can be false if you don't want to use the status-LED

## MQTT-config:
- <b>Broker:   </b>         The Broker's IP-Adress
- <b>Client:   </b>         Set a unique client name for each device -> Topics are created from that name
- <b>md_pin:   </b>         Pin for sensor (currently not used)
- <b>Port: </b>             The MQTT Network-Port (1883 by default)
- <b>PW: </b>               MQTT Password, if needed
- <b>User:</b>              MQTT User, if needed
- <b>publish_in_json:</b>   Publish Messages in json-format? (true by default)
- <b>topics:</b>            A list of topics to subscribe

## LightControl_settings
- <b> autostart: </b>        Set the LEDs to the last saved state when power on (true by default)
- <b> bytes_per_pixel:</b>  Set Bytes per pixel (i.e. 3 for RGB, 4 for RGBW, ...)
- <b>led_pin:</b>          LEDs Data-Pin
- <b>led_qty: </b>         Quantity of the used LEDs

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
