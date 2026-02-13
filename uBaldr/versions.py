from mqtt_Client import version as Client
from uWifi import version as Wifi
from order import version as Order
from ntp_simple import Version as NTP
from LightControl import version as LC
from json_config_parser import version as json
from mqtt_handler import version as mqtt_handler
from Led_controller import version as led_controller
from logger import version as logger
from umqtt_simple import version as umqtt
import sys

version = [1,3,1, 'c']

platform = sys.platform

versions = {
    'Client': Client, 
    'Wifi': Wifi, 
    'order': Order, 
    'ntp_simple': NTP, 
    'LightControl': LC, 
    'json': json, 
    'mqtt_handler': mqtt_handler,
    'Led_controller': led_controller,
    'logger': logger,
    'main': [7,2,1],
    'last umqtt_simple': [f'{umqtt[0]}/{umqtt[1]}/{umqtt[2]}'],
    'Platform': [str(platform)]
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

# Under construction:
def version_check(module, requested, level):
    module_version = module
    if module_version[level] == requested[level]:
        return True
    else:
        return False

def version_string(sub):
    return str(f'{sub[0]}.{sub[1]}.{sub[2]}')