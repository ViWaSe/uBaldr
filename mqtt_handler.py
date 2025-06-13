from umqtt_simple import MQTTClient
from logger import Log
import utime as time

version = '1.1'

class MQTTHandler:
    def __init__(self, client_id, broker, user=None, password=None):
        self.client_id = client_id
        self.broker = broker
        self.user = user
        self.password = password
        self.client = None

    def connect(self):
        # Establish MQTT-Connection
        try:
            self.client = MQTTClient(self.client_id, self.broker, user=self.user, password=self.password)
            self.client.set_callback(self.on_message)
            self.client.set_last_will(topic=f"{self.client_id}/status", msg='{"msg": "offline"}', retain=True)
            self.client.connect()
            Log('MQTT', '[ INFO  ]: MQTT connection established!')
            return True
        except Exception as e:
            Log('MQTT', f'[ FAIL  ]: Connection failed - {e}')
            return False

    def on_message(self, topic, msg):
        try:
            nachricht = msg.decode('utf-8')
            # Log('MQTT', f'[ INFO  ]: Received message: {nachricht}')
            
            import ujson as json
            payload = json.loads(nachricht)

            if payload.get('sub_type') == 'admin' and payload.get('command') == 'get_update':
                modules = payload.get('module')  # string or list
                base_url = payload.get('base_url', 'PUT_INYOUR_URL')
                self.perform_ota_update(modules, base_url)
                return

            from order import run
            ans = run(nachricht)
            if ans:
                self.publish(f"{self.client_id}/status", str(ans))

        except Exception as e:
            Log('MQTT', f'[ FAIL  ]: Message processing failed - {e}')

    def subscribe(self, topic):
        # Subscribe-function
        if self.client:
            self.client.subscribe(topic)
            Log('MQTT', f'[ INFO  ]: Subscribed to {topic}')
            self.publish(self.client_id, 'online')

    def publish(self, topic, message, retain=False):
        # Publish-function
        if self.client:
            self.client.publish(topic, message, retain=retain)
            Log('MQTT', f'[ INFO  ]: Published message to {topic}: {message}')

    def check_msg(self):
        # Check for incoming messages, reconnect if needed
        try:
            if self.client:
                self.client.check_msg()
        except Exception as e:
            Log('MQTT', f'[ ERROR ]: MQTT error - {e}')
            self.reconnect()

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            Log('MQTT', '[ INFO  ]: MQTT connection closed')
    
    def reconnect(self):
        Log('MQTT', '[ RECONNECT ]: Attempting to reconnect...')
        self.disconnect() 
        while not self.connect(): 
            Log('MQTT', '[ RECONNECT ]: Reconnect failed, retrying in 5 seconds...')
            time.sleep(5) 
        Log('MQTT', '[ RECONNECT ]: Reconnected successfully!')
    
    # Update-function
    def perform_ota_update(self, module_name='all', base_url='BASE_URL'):
        import urequests as requests
        import os

        def update_single_module(name, url):
            try:
                Log('OTA', f'[ INFO  ]: Downloading {name} from {url}')
                response = requests.get(url)
                if response.status_code == 200:
                    with open(name, "w") as f:
                        f.write(response.text)
                    Log('OTA', f'[ INFO  ]: {name} updated successfully')
                    self.publish(f"{self.client_id}/status", f'{{"msg": "{name} update successful"}}')
                else:
                    Log('OTA', f'[ FAIL  ]: Could not download {name}')
                    self.publish(f"{self.client_id}/status", f'{{"msg": "update failed for {name}"}}')
            except Exception as e:
                Log('OTA', f'[ FAIL  ]: Update error for {name} - {e}')
                self.publish(f"{self.client_id}/status", f'{{"msg": "update error for {name}: {e}"}}')

        if isinstance(module_name, list):
            for mod in module_name:
                url = base_url + mod
                update_single_module(mod, url)
            Log('OTA', '[ INFO  ]: Update done. Will now reboot ...')
            import machine
            machine.reset()
        else:
            url = base_url + module_name
            update_single_module(module_name, url)
            if module_name.lower() == "main.py":
                import machine
                machine.reset()