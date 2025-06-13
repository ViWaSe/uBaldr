# Smarthome Order-Modul by vwall

Version = '5.3'

import LightControl as LC
import switch
import json
from logger import Log

class proc(object):
    def __init__(
            self, 
            data='temp.json'
            ):   
        with open (data) as f:    
            self.data = json.load(f)
    
    # Device_control:
    def dev_control(self):
        dev_name    = self.data['device']
        command     = self.data['command']
        payload     = self.data['payload']

        if command == 'switch':
            switch.on_off(dev_name, payload)
        elif command == 'timer':
            switch.timer(dev_name, int(payload))
        elif command == 'pin':
            pin = self.data('pin')
            switch.pin_control(pin, payload)
        else:
            pass
    
    # Light control function:
    def LC(self):
        command 	    = self.data['command']
        payload 	    = self.data['payload']
        speed   	    = self.data['speed']
        color_format 	= self.data['format']

        if color_format == 'hex':
            from hex_to_rgb import hex_to_rgb
            color = hex_to_rgb(str(payload))
        else:
            color = payload
        
        # Change the LED-Pin if set in order string:
        try:
            LC.set_led(new_device=self.data['device']) 
        except:
            pass
        
        # Run the command in LightControl
        if command == 'dim':
            LC.dim(payload, speed).set()
        elif command == 'line':
            LC.line(color, speed)
        elif command == 'on_off':
            LC.on_off(payload)
        elif command == 'get_lvl':
            level = LC.ret_dim()
            return level
        else:
            return 'LC: Command not found'
        Log('Order', '[ INFO ]: ' + str(command))
        return True
    
    # admin-functions
    def admin(self):
        if self.data['command'] == 'echo':
            return 'alive'
        
        elif self.data['command'] == 'offline':
            Log('MQTT', '[ INFO ]: Broker is offline. Probably shutdown.')
            return 'conn_lost'
        
        elif self.data['command'] == 'get_conf':
            from PicoClient import send_json as send
            send('config.json')
        
        elif self.data['command'] == 'get_version':
            from PicoClient import Version
            if self.data['payload'] == 'all':
                return Version
            else:
                ver = self.data['payload']
                return Version[ver]
        
        elif self.data['command'] == 'change_qty':
            LC.set_led_qty(self.data['new'])
            LC.re_initiate_pixel()
            Log('LC', '[ INFO ]: LED-Qty changed to '+str(self.data['new']))
            return 'OK'

        elif self.data['command'] == 'get_qty':
            qty = LC.pixel
            return qty            
        
        else:
            pass

# Order-processing function
def run(json_string):

    # Create a tmp.json file from incoming string
    tmp = open('temp.json', 'w')
    tmp.write(json_string)
    tmp.close()
    
    with open ('temp.json') as f:    
        data = json.load(f)
    order = data['Type']  
    order_instance = proc()
    try:
        call = getattr(order_instance, order)()
        return call
    except:
        return 'Command is not found. Check your input!'
    

# Beispiele:
LC_string       = '{"Type": "LC", "device": "led_pin", "command": "line", "payload": [0,0,0,0], "speed": 5, "format": "rgbw"}'

