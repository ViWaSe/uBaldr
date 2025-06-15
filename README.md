# uBaldr
This is a Micropython Smarthome / IoT-project using Raspberry PicoW or ESP-32 microcontroller.

# Purpose
You can use this project to control Neopixel-LEDs via the MQTT-Protocoll. A MQTT-Broker is needed to run the project and can i.E. be realized by a Raspberry Pi.
JSON-Strings are used for communication. Please see documentation pdf for more info!

# Features
- Set Color by line-animation (pixel by pixel) with defined speed. Supported formats: hex, [r,g,b] and [r,g,b,w]
- Dim light with defined speed
- OTA-Updates
- Change settings via MQTT-Message
- Log-function
- NTP

# Supported Hardware
- uBaldr fully supports Raspberry PicoW and ESP32 Microcontrollers. Note that you need to change the onboard-led-settings depending on your device.
- NeoPixel-LEDs are supported in RGB, RGBW and WW/CW Variants

# Usage
The Project works with 2 MQTT-Topics. device/order ist the order you send to the client. Messages from the client are published to device/status.
  - Example 1 - Set the color of your LED-Strip to rgb-red (255,0,0) by line-animation. You can set a speed (pause between pixels in ms).
    - JSON-String to device/order:
    > {"sub_type": "LC", "command": "line", "payload": [255,0,0], "format": "rgb", "speed": 5}
    - Answer from device/status: True
  - Example 2 - dim the light to 5% with 1ms between %-steps
    - JSON-String:
    > {"sub_type": "LC", "command": "dim", "payload": 5, "speed": 1}
    - Answer from device/status: True

# Micropython-Files
You find everything you need to copy to your µPython-device in the uBaldr-Folder.
Change the config.json and fill in your wifi-settings and MQTT-settings before start!

# Documentaion
I tried my best to write a documentation on how to use the project.
Please let me know if you have questions / improvement-suggestions or found bugs. 

Hope you enjoy my first project!
