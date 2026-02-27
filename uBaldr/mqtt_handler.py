# New MQTT-Handler Module for Baldr V6.x

version = [2,3,0, 'alfa-5']

from umqtt_simple import MQTTClient
import utime as time
import json
import ujson
import logger
from order import run

# If typing don't exist:
try:
    from typing import Optional, Any
except ImportError:
    Optional = Any = object

class MQTTHandler:
    def __init__(
            self, 
            client_id, 
            broker, 
            user=None, 
            password=None,
            pinjson=False
            ):
        
        """
        Parameter:
            client_id (str): Unique ID of the Device / Client.
            broker (str): IP-Adress or inet-adress of the MQTT-Broker.
            user (str): Username, if authorization is used.
            password (str): password, if authorization is used.
            pinjason (bool): If True, messages will be published in JSON-Format
        """

        self.client_id = client_id
        self.broker = broker
        self.user = user
        self.password = password
        self.client: Optional[MQTTClient] = None # type: ignore
        self.subscribed_topic = None
        self.injson = pinjson
        self.received = False

        self.event = logger.Create('MQTT_Handler', '/log/')
        self.ota_event = logger.Create('OTA', '/log/')
        
        self.last_ping = time.time()
        self.ping_interval = 15

        self.ip_adress = ''

    

    # Connection ---------------------------------------------------------------------------------------------------------------
    def connect(self):
        """
        Establish the MQTT-Connection
        """
        try:
            self.client = MQTTClient(self.client_id, self.broker, user=self.user, password=self.password, keepalive=20)
            self.client.set_callback(self.on_message)
            self.client.set_last_will(topic=f"{self.client_id}/status", msg="offline", retain=False)
            self.client.connect()
            self.event.log('I', 'MQTT connection established!')
            self.send_alive()
            return True
        except Exception as e:
            self.event.log('E', f'Connection failed - {e}')
            return False
    
    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.event.log('I', 'MQTT connection closed')
    
    def reconnect(self):
        self.event.log('I', 'Attempting to reconnect...')
        try:
            self.disconnect()
        except:
            pass
        while True: 
            try: 
                self.connect()
                break
            except Exception as e:
                self.event.log('E', 'Reconnect failed, retrying in 5 seconds...')
                time.sleep(5) 
        self.event.log('I', 'Reconnected successfully!')
        self.subscribe(self.subscribed_topic)
    
    def subscribe(self, topic):
        self.subscribed_topic = topic
        if self.client:
            self.client.subscribe(topic)
            self.event.log('I', f'Subscribed to {topic}')
            self.send_alive()

    # TODO: Remove the topic from the topics-list and save it to the JSON
    def unsubscribe(self, topic, remove=False):
        self.client.unsubscribe(topic)
        if remove:
            pass
    
    # Message functions---------------------------------------------------------------------------------------------------------

    # Publish to a topic
    def publish(
            self, 
            topic, 
            message, 
            retain=False,
            use_raw_string=False,
            ):
        if not self.client:
            return
        if not use_raw_string:
            injson = self.injson
            if injson:
                payload = {
                    "msg": message.get("msg"),
                    "is_err_msg": message.get("is_err_msg"),
                    "origin": message.get("origin")
                }
                self.client.publish(topic, json.dumps(payload), retain=retain)
            else:
                self.client.publish(topic, str(message.get("msg")), retain=retain)
        else:
                self.client.publish(topic, json.dumps(message), retain=retain)
            # Log('MQTT', f'[ INFO  ]: Published message to {topic}: {message}')

    # process incomming messages
    def on_message(
            self, 
            topic, 
            msg
            ):
        if not msg:
            pass
        try:
            in_message = msg.decode('utf-8')
            topic_string = topic.decode('utf-8')
            self.set_rec(True)
            
            if topic_string == f'uBaldr/{self.client_id}/echo':
                self.send_alive()
                return
            
            payload = ujson.loads(in_message)
            if payload.get('sub_type') == 'admin' and payload.get('command') == 'get_update':
                modules = payload.get('module') 
                base_url = payload.get('base_url')
                self.perform_ota_update(modules, base_url)
                return

            ans = run(in_message)
            
            if ans:
                if ans.get('origin') == 'logger':
                    topic = f'uBaldr/{self.client_id}/status/log'
                else:
                    topic = f'uBaldr/{self.client_id}/answer'
                if ans == 'conn_lost':
                    self.event.log('I', 'Broker is offline under normal conditions. Trying to reconnect...')
                    self.reconnect()
                else:
                    self.publish(f'{topic}', ans)
            if not ans:
                ans = '>> No order processing <<'

        except Exception as e:
            self.event.log('E', f'Message processing failed - {e}')
            self.event.log('I', f'Message: {msg} | Order result: {ans}')

    # Check for incoming messages, reconnect if needed
    def check_msg(self):
        try:
            if self.client:
                self.mqtt_ping()
                self.client.check_msg()
        except Exception as e:
            self.event.log('E', f'MQTT error during check_msg() - {e}')
            self.reconnect()
    def wait_msg(self):
        if self.client is not None:
            self.client.wait_msg()

    # Utils --------------------------------------------------------------------------------------------------------------------
    def send_alive(self):
        data = {
            "status": "online",
            "uptime": self.get_uptime(),
            "ip": self.ip_adress,
            "mqtt_handler_version": version,
            "client_id": self.client_id
        }
        self.publish(f'uBaldr/{self.client_id}/status', data, use_raw_string=True)

    def get_uptime(self):
        millis = time.ticks_ms()

        secs = millis // 1000
        mins = secs // 60
        hrs = mins // 60
        days = hrs // 24

        # return string in format 1d 04h 20m
        return f'{days}d {hrs % 24:02d}h {mins & 60:02d}m'

    def mqtt_ping(self):
        current_time = time.time()
        if current_time - self.last_ping > self.ping_interval:
            try:
                self.client.ping()
                self.last_ping = current_time
            except Exception as e:
                self.event.log('E', f'Ping failed - {e}')
                self.reconnect()

    def set_rec(self, state):
        self.received=state

    def get_rec(self):
        return self.received
    
    def set_publish_in_json(self, state):
        self.injson = state  

    def set_ip(self, ip):
        self.ip_adress = ip

    # Update-function ----------------------------------------------------------------------------------------------------------
    def perform_ota_update(
            self, 
            module_name='all', 
            base_url='BASE_URL'
            ):
        
        """
        Performs OTA-Update.

        Parameter:
            modul_name (str): Name of the target-Module (e.g. NTP.py). If set to 'all', all modules will be updated
            base_url: The location of the update-Files
        """

        import urequests as requests
        import os

        if module_name == 'all':
            module_name = [
                'main.py',
                'mqtt_handler.py',
                'LightControl.py',
                'uWifi.py',
                'mqtt_Client.py',
                'order.py',
                'logger.py',
                'Led_controller.py',
                'json_config_parser.py',
                'ntp_simple.py',
                'versions.py'
                ]

        def update_single_module(name, url):
            try:
                self.ota_event.log('I', f'Downloading {name} from {url}')
                response = requests.get(url)
                if response.status_code == 200:
                    with open(name, "w") as f:
                        f.write(response.text)
                    self.ota_event.log('I', f'{name} updated successfully')
                    self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": f'{name} update was successful!', "is_err_msg": False, "origin": "OTA_Update"})
                else:
                    self.ota_event.log('E', f'Could not download {name}')
                    self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": f'update failed for {name}', "is_err_msg": True, "origin": "OTA_Update"})
            except Exception as e:
                self.ota_event.log('F', f'Update failed for {name} - {e}')
                self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": f'update error for {name}: {e}', "is_err_msg": True, "origin": "OTA_Update"})

        if isinstance(module_name, list):
            anz = len(module_name)
            act = 0
            for mod in module_name:
                url = base_url + mod
                update_single_module(mod, url)
                
                # send update progress to the broker
                act += 1
                perc = round((act/anz*100),0)
                self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": f"update", "progress": perc, "is_err_msg": False, "origin": "OTA_Update"}, use_raw_string=True)
            
            self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": "OTA-Update done! Will now reboot...", "is_err_msg": False, "origin": "OTA_Update"})       
            self.ota_event.log('I', 'Update done. Will now reboot ...')
            import machine
            machine.reset()
        
        else:
            self.publish(f"uBaldr/{self.client_id}/status/update", {"msg": "No module updated. Please send the modules in list-format! Try the provided string from github.", "is_err_msg": True, "origin": "OTA_Update"})