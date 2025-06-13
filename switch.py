import utime as time
from machine import Pin
from json_config_parser import config, create

Version = '1.0.1'

settings    = config('/params/config.json', layers=2)

# Load the status file. If no status file exists, create new one:
try:
    status  = config('switch.json', layers=1)
except FileNotFoundError:
    create('switch.json', '{"dev_1":[{"Pin": 14,"Type": "PULL_DOWN", "IN_OUT": "OUT"}]}')
    status  = config('switch.json', layers=1)

def save_status(device, status):
    status.save_param(device, status) 

def on_off(device, value):
    out_1 = settings.get(device, 'Pin')
    out = Pin(out_1, Pin.OUT, value=0)
    if value == 1:
        out.on()
    elif value == 0:
        out.off()

def timer(device, value):
    out_1 = settings.get(device, 'Pin')
    out = Pin(out_1, Pin.OUT, value=0)
    out.on()
    time.sleep_ms(value)
    out.off()

def pin_control(pin, value):
    out = Pin(pin, Pin.OUT, value=value)

def pwm_control(device, value):
    # V1.1
    pass
    