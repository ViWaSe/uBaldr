

<img width="1024" height="1024" alt="BaldrOS" src="https://github.com/user-attachments/assets/14234b7b-3ecf-4e38-92b5-b50994df123f" />

# uBaldr
This is a Micropython Smarthome / IoT-project using Raspberry PicoW or ESP-32 microcontroller.

# Purpose
You can use this project to control Neopixel-LEDs via the MQTT-Protocoll. A MQTT-Broker is needed to run the project and can i.E. be realized by a Raspberry Pi.
JSON-Strings are used for communication. Please see documentation pdf for more info!

# Features
- Set Color by line-animation (pixel by pixel) with defined speed. Supported formats: hex, [r,g,b] and [r,g,b,w]
- Set Color by smooth animantion (all pixel at same time). Parametere are the same as by line-animation
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
I will add a full manual to the first stable release.

# OTA-Update
To trigger an OTA-Update, send this JSON-String to the device/order Topic:
>{
  "sub_type": "admin",
  "command": "get_update",
  "module": [
    "main.py",
    "LightControl.py",
    "PicoClient.py",
    "PicoWifi.py",
    "mqtt_handler.py",
    "order.py",
    "logger.py"
  ],
  "base_url": "https://raw.githubusercontent.com/ViWaSe/uBaldr/23f1a65849bd52473a034db57b25b3bd1d537e0f/uBaldr/"
}

Hope you enjoy my first project!
