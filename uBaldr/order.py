# Smarthome Order-Modul by vwall

version = [7,0,1,'a']

import json
from LightControl import LC as LightControl
import logger
from hex_to_rgb import hex_to_rgb

event = logger.Create('order', '/log')

class Proc:
    def __init__(self, data=None):
        if data is None:
            raise ValueError("Data error.")
        self.data = data
    
    def make_result(
            self,
            msg,
            is_error=False,
            origin='Unknown'
    ):
        return {"msg": msg, "is_err_msg": is_error, "origin": origin}
    
    # LightControl-functions
    def LC(self):
        command = self.data['command']
        payload = self.data['payload']

        if 'dir' in self.data:
            dir = self.data['dir']
        else:
            dir=0
        
        if isinstance(payload, list):
            color = payload
        if isinstance(payload, str):
            try:
                color = hex_to_rgb(str(payload))
            except ValueError:
                return self.make_result('Failed! Payload is not list or hex!', is_error=True, origin='LightControl')
        
        if 'speed' in self.data:
            speed   = self.data['speed']
        else:
            speed = 5
        
        if 'steps' in self.data:
            steps = self.data['steps']
        else:
            steps = 50

        command_map = {
            'dim': lambda: LightControl.set_dim(payload, speed),
            'line': lambda: LightControl.line(color, speed, dir),
            'smooth': lambda: LightControl.set_smooth(color, speed, steps) 
        }
        
        if command in command_map:
            command_map[command]()
            return self.make_result(msg=True, is_error=False, origin='LightControl')
        else:
            event.log('E', f'Command >>{command}<< not found!')
            return self.make_result(msg='Command not found!', is_error=True, origin='LightControl')

    # Admin-Functions
    def admin(self):

        command = self.data['command']

        if 'new_value' in self.data:
            new_value = self.data['new_value']

        command_map = {
            'echo': lambda: self.echo(),
            'offline': lambda: self.handle_offline(),
            'alive': lambda: self.ok(),
            'get_version': lambda: self.get_version(),
            'change_led_qty': lambda: self.change_led_qty(new_value),
            'get_qty': lambda: LightControl.pixel,
            'set_autostart': lambda: self.change_autostart_setting(new_value),
            'get_log': lambda: self.get_log(),
            'set_GMT_wintertime': lambda: self.change_GMT_time(new_value),
            'set_GMT_offset': lambda: self.change_GMT_time(new_value),
            'get_timestamp': lambda: self.get_timestamp(),
            'reboot': lambda: self.reboot(),
            'get_sysinfo': lambda: self.get_sysinfo(),
            'onboard_led_active': lambda: self.onboard_led_active(new_value),
            'publish_in_json': lambda: self.pinjson(new_value)
        }
        
        return command_map.get(command, lambda: self.make_result(msg=f'Command not found: {command}', is_error=True, origin="command_handler"))()
    
    def echo(self):
        return self.make_result(msg='alive', origin='admin')
    
    def ok(self):
        return self.make_result(msg='ok', origin='admin')
    
    def pinjson(self, value: bool):
        from mqtt_Client import settings, publish_in_Json
        if publish_in_Json != value:
            settings.save_param(group='MQTT-config', param='publish_in_json', new_value=value)
            publish_in_Json = value
        return self.make_result(msg='Setting changed and takes effect after reboot.', is_error=False, origin='admin')

    # Log when Broker is offfline
    def handle_offline(self):
        return 'conn_lost'

    def get_sysinfo(self):
        import sys
        platform = sys.platform
        return self.make_result(msg=f'Platform: {platform}', is_error=False, origin='admin')

    # Reboot-request
    def reboot(self):
        event.log('I', 'Reboot requested. Will now call a machine.reset()')
        import machine
        machine.reset()
    
    def onboard_led_active(self, new_state):
        from uWifi import Client
        led_onboard = Client.get_led()
        led_onboard.set_active(new_state)
        return self.make_result(msg=f'onboard_led active setting -> {new_state}', is_error=False, origin='admin')
    
    # Get Timestamp from NTP-Module
    def get_timestamp(self):
        import NTP
        time = NTP.NTP()
        return self.make_result(msg=time.timestamp(), is_error=False, origin='admin/NTP')
    
    # Change NTP-Settings (Wintertime and GMT-Osffset)
    def change_GMT_time(
            self, 
            winter=True, 
            GMT_adjust=3600
            ):
        
        from json_config_parser import config
        time_setting    = config('/params/time_setting.json', layers=1)
        use_winter_time = time_setting.get(param='use_winter_time')
        GMT_offset      = time_setting.get(param='GMT_offset')
        
        if winter != use_winter_time:
            time_setting.save_param(param='use_winter_time', new_value=winter)
            #Log('NTP', 'I', f'Changed Wintertime to {winter}')
            return self.make_result(msg=f'set wintertime to {winter}. Changes will take effect after reboot', is_error=False, origin='admin/NTP')
        
        if GMT_adjust != GMT_offset:
            time_setting.save_param('GMT_offset', GMT_adjust)
            #Log('NTP', 'I', f'Adjusted GMT-Offset to {GMT_adjust}')
            return self.make_result(msg=f'set GMT-Offset to {GMT_adjust}. Changes will take effect after reboot', is_error=False, origin='admin/NTP')

    def get_version(self):
        import versions
        if self.data['sub_system'] == 'all':
            return self.make_result(msg=versions.all(), is_error=False, origin='admin/versions')
        else:
            return self.make_result(msg=versions.by_module(self.data['sub_system']), is_error=False, origin='admin/versions') 

    # Change LED-quantity
    def change_led_qty(self, new_value):
        LightControl.change_pixel_qty(new_value)
        return self.make_result(msg=f'NeoPixel Quantity changed to {new_value}', origin='LightControl')
    
    # Change Autostart-setting
    def change_autostart_setting(self, new_value):
        LightControl.change_autostart(new_value)
        return self.make_result(msg=f'NeoPixel Autostart changed to {new_value}', origin='LightControl')

    def get_log(self):
        path = f'/log/{self.data['module']}.log'
        logs = event.get_log(str(path))
        return self.make_result(msg=logs, is_error=False, origin='admin')
    
    def set_mqtt(self):
        broker = self.data['broker']
        client = self.data['client']
        user = self.data['usr']
        pw = self.data['pw']

        from json_config_parser import config
        conf = config('/params/config.json', 2)
        conf.save_param('MQTT-config', 'Broker', broker)
        conf.save_param('MQTT-config', 'Client', client)
        conf.save_param('MQTT-config', 'User', user)
        conf.save_param('MQTT-config', 'PW', pw)

        return self.make_result(msg=f'Changed MQTT-Settings. New Broker: {broker} | New Client-Name: {client} The client will no longer be reachable via this broker after a reboot!')

# Run a JSON-String
def run(json_string):
    try:
        data = json.loads(json_string)
        order_instance = Proc(data)

        # Get the Order-Type from JSON
        if 'sub_type' in data:
            order = data['sub_type']
        else:
            order = data['Type']
        
        call = getattr(order_instance, order)()
        return call
    except KeyError as e:
        event.log('E', f'Key-Error / Key not found - {e}')
        return order_instance.make_result(msg=f"Key not found: {e}", is_error=True, origin='order_processing')
    except AttributeError:
        event.log('E', f'The sub-type >{order}< is not a known instance')
        return order_instance.make_result(msg=f"Command not found!", is_error=True, origin='order_processing')
    except Exception as e:
        event.log('E', f'Unknown Error - {e}')
        return order_instance.make_result(msg=f"Unknown Error: {e}", is_error=True, origin='order_processing')

