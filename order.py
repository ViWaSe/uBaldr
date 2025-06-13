# Smarthome Order-Modul by vwall
# Processing json-strings
# Fixed the mqtt-json-issue
# Unfortunately it is not supported, to use the mqtt-string directly, so we must take a little detour with a temp-file
Version = '5.1j'

import LightControl as LC
import json
from PicoWifi import Log

# Create a class to process the incoming data (json-string):
class proc(object):
    def __init__(
            self, 
            data
            ):
        self.tmp = open('temp.json', 'w')
        self.tmp.write(data)
        self.tmp.close()
        with open ('temp.json') as f:    
            self.data = json.load(f)
        self.type = self.data['Type']
        # print(self.data, self.type, self.data['command'], self.data['payload'])

    # Sort the data by type and call the right program:     
    def run(self):
        pass
        if self.type == 'admin':
            self.admin()
        elif self.type == 'LC':
            self.LC()
        elif self.type == 'relay':
            self.relay()
        elif self.type == 'motor':
            self.motor()
        else:
            pass
        return 'ready'
    
    # Light control: process the data and call the Light control program with the command, payload and speed:
    def LC(self):
        command 	= self.data['command']
        payload 	= self.data['payload']
        speed   	= self.data['speed']
        c_format 	= self.data['format']

        if c_format == 'hex':
            from hex_to_rgb import hex_to_rgb
            color = hex_to_rgb(str(payload))
        else:
            color = payload
        
        # Set the device if device is specified in the string (name must be present in config.json. Otherwise it will use the standard led_pin variable or the last used led-device)
        # The order is logged in the Pico.log file
        try:
            LC.change_led(self.data['device'])
            Log(
                'New LC-order - command: ' + command + 
                ' | payload: ' + str(payload) + 
                ' | speed: ' + str(speed) + 
                ' | device: ' + self.data['device']
                )
        except:
            Log(
                'New LC-order - command: ' + command + 
                ' | payload: ' + str(payload) + 
                ' | speed: ' + str(speed))
        
        # Sort by command and run Light-control. Currently only 2 types of commands (line and dim).
        if command == 'dim':
            LC.dim(payload, speed).set()
        elif command == 'line':
            LC.line(color, speed)
        else:
            return 'Command not found'
        Log('fin')
    
    # Some admin-functions, can be extended
    def admin(self):
        if self.data['command'] == 'echo':
            return 'alive'
        elif self.data['command'] == 'offline':
            Log('Broker is offline')
            return 'lost'
        elif self.data['command'] == 'conf':
            return 'send_config'
        else:
            pass
    
    # Under construction / not used
    def relay(self):
        pass

    def motor(self):
        pass
        
    

# Beispiele:
LC_string       = '{"Type": "LC", "device": "led_pin", "command": "line", "payload": [0,0,0,0], "speed": 5, "format": "rgbw"}'
LC_string       = '{"Type": "LC", "command": "line", "payload": [0,0,0,0], "speed": 5, "format": "rgbw"}'
LC_string       = '{"Type": "LC", "command": "line", "payload": "FF0000", "speed": 5, "format": "hex"}'
admin_string    = '{"Type": "admin", "command": "echo"}'
Bsp_string1     = '{"Type": "relay", "device": "R1", "command": "on"}'
Bsp_string1     = '{"Type": "motor", "device": "M1", "command": "move", "target": 2000, "speed": 5, "EOF": 1800, "EOS": 2000}'

LC_string       ='{"Type": "LC", "start": <FIRST SEGMENT>, "end": <LAST SEGMENT>, "animation": <None, "line", "swap", "dim">, "payload": <LIST (4x 0-255) OR NUMBER (0-100) OR HEX-CODE>, "speed": 5}'
