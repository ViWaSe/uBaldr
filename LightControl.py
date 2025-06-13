# LightControl
# Supports WS2812B & SK2812 rgb + rgbw (adjust the "bytes_per_pixel" value in the config-file (3=rgb, 4=rgb+w))
# neopixel-configuration is saved in config.json file
# 05.12.2023 by vwall

Version='5.1j'

import utime as time
from neopixel import NeoPixel
from machine import Pin
from json_config_parser import config

# Save current status
def save_color(cache):
    status.save_param('status', 'color', cache)

# Load configuration from config file
settings    = config('config.json', 2)
status      = config('status.json', 1)
cache       = status.get(param='color')
led_pin     = settings.get('LightControl_settings', 'led_pin')
pixel       = settings.get('LightControl_settings','num_of_leds')
PixelByte   = settings.get('LightControl_settings','bytes_per_pixel')
autostart   = settings.get('LightControl_settings','autostart')

level       = 0

# Initiate LED-Pin and Neo-Pixel settings
led = Pin(led_pin, Pin.OUT, value=0)
np  = NeoPixel(led, pixel, bpp=PixelByte) # bpp = bytes per pixel

# Function to change LED-Pin -> name must be present in config.json!
def set_led(pin='led_pin'):
    global np
    try:
        led_pin = settings.light_control(pin)
        led     = Pin(led_pin, Pin.OUT, value=0)
        np      = NeoPixel(led, pixel, bpp=PixelByte)
        return 'success'
    except:
        return 'Name not present in config file!'

# Set all LEDs (Basic function)
def static(color, level=1):
    global pixel, cache
    color=list(color)
    if len(color)<4:
        color.append(0)
    for i in range (pixel):
        np[i] = (
            int(color[0]*level), 
            int(color[1]*level), 
            int(color[2]*level), 
            int(color[3]*level)
            )
    np.write()

# clear all pixels
def clear():
    global pixel
    for i in range (pixel):
        np[i] = (0, 0, 0, 0)
    np.write()

# Dim-Functions
class dim():
    def __init__(
        self, 
        target, 
        speed=1,
        level=level 
    ):
        self.target = target
        self.speed  = speed
        self.level  = level
        self.actual = self.level * 100
    
        if self.target < self.actual:
            self.ramp_dn()
        elif self.target > self.actual:
            self.ramp_up()
        self.save()

    def ramp_up(self):
        global level, cache
        actual = level * 100
        while actual < self.target:
            self.actual += 1
            level = actual/100
            static(cache, (level))
            time.sleep_ms(self.speed)

    def ramp_dn(self):
        global level, cache
        actual = level * 100
        while actual > self.target:
            self.actual -= 1
            level = actual/100
            static(cache, (level))
            time.sleep_ms(self.speed)

    def save(self):
        status.save_param(param='dim_status', data=self.target)

# set color to a single pixel
def single(colour, segment):
    global cache
    colour=list(colour)
    if len(colour)<4:
        colour.append(0)
    np[segment] = (
        int(colour[0]*level), 
        int(colour[1]*level), 
        int(colour[2]*level), 
        int(colour[3]*level)
        )
    np.write()

# Set color with line-animation
def line(color, speed=5, dir=0, gap=1, start=0):
    global pixel, cache
    speed = int(speed)
    line = start
    color=list(color)
    if len(color)<4:
        color.append(0)
    if dir == 0:
        while line < pixel:
            np[line] = (
                int(color[0]*level), 
                int(color[1]*level), 
                int(color[2]*level), 
                int(color[3]*level)
                )
            np.write()
            line += gap
            time.sleep_ms(speed)        
    elif dir == 1:
        while line > 0:
            np[line] = (
                int(color[0]*level), 
                int(color[1]*level), 
                int(color[2]*level), 
                int(color[3]*level)
                )
            line -= gap
            np.write()
            time.sleep_ms(speed)
    cache = color
    status.save_param(param='color', data=cache)
    return cache

# Load the last known status
if autostart == True:
    dim_status = status.get(param='dim_status')
    lvl=dim(dim_status)
    lvl.set()

