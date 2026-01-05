from mqtt_Client import version as Client
from uWifi import version as Wifi
from order import version as Order
from NTP import Version as NTP
from LightControl import version as LC
from json_config_parser import version as json
from mqtt_handler import version as mqtt_handler
from Led_controller import version as led_controller
from logger import version as logger
import sys

version = [1,3,0]

platform = sys.platform

versions = {
    'Client': Client, 
    'Wifi': Wifi, 
    'order': Order, 
    'NTP': NTP, 
    'LightControl': LC, 
    'json': json, 
    'mqtt_handler': mqtt_handler,
    'Led_controller': led_controller,
    'logger': logger,
    'main': [7,1,1, 'a'],
    'Platform': platform
    }

def by_module(module):
    sub = versions[module]
    if type(sub) is list:
        if len(sub) < 4:
            return str(f'{sub[0]}.{sub[1]}.{sub[2]}')
        else:
            return str(f'{sub[0]}.{sub[1]}.{sub[2]}{sub[3]}')
    else:
        return versions[module]

def all():
    return versions

def compatibility_check():
    release_code=20251007
    pass

def version_string(sub):
    return str(f'{sub[0]}.{sub[1]}.{sub[2]}')