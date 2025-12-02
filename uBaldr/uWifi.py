# Wifi network module for Prapberry pi pico and ESP-32
# configuration stored in JSON-File
# works with micropython v1.21.0 and higher
# TODO: Implement the check_connection-function

version = [7,1,1]

import utime as time
import network, machine
from json_config_parser import config
import logger
from Led_controller import LedController
import sys

class Client:
    led_global = None

    def __init__(
            self,
            use_config_json=True,
            config_file='/params/config.json',
            wlanSSID='',
            wlanPW='',
            hostname='baldr',
            use_onboard_led=True,
            led_pin=0,
            led_inverted=False,
            testhost='127.0.0.1',
            max_attempts=5,
            loglevel=0
            ):
        
        """
        Create a Wifi-client. This class is used to connect the u-Python-Device to the Wifi-Network.
        You can use a JSON-File to store the settings or use this class directly without JSON.

        Parameters:
            use_config_json (bool): Is a JSON-File used to store the settings? If 'True', you can leave the rest empty.
            config_file (str): Location of the config-File (JSON).
            wlanSSID (str): SSID of the target-Wifi.
            wlanPW (str): Password of the target Wifi.
            hostname (str): Set a hostname if needed.
            use_onboard_led (bool): Use the onboard-LED as status-indicator.
            led_pin (int): Pin of the Onboard-LED.
            led_inverted (bool): Inverted LED-Setting. False by default.
            testhost (str): Target-Adress to test the connection.
            max_attempts (int): Maximum number of retries if the connection fails.
            loglevel (int): Set the loglevel for events. 0=normal, 1=debug, 2=off

        Methods:
        --------
            connect():
                Connects the client to the Wifi with the specified settings
            save_ip():
                Saves the IP-Adress to the JSON-Config-File if JSON-Config is used.
            error_handler(errno):
                Converts the wlan-error-number to an error-message
        
        Usage:
        ------
            1. Create the Object wifi = client(...)
            2. To connect, call wifi.connect()
            3. To check status, call wifi.check_status()
        """

        if use_config_json:
            self.settings    = config(config_file)
            self.wlanSSID    = self.settings.get('Wifi-config', 'SSID')
            self.wlanPW      = self.settings.get('Wifi-config', 'PW')
            self.hostname    = self.settings.get('Wifi-config', 'Hostname')

            self.led_active  = self.settings.get('Wifi-config', 'led_active')
            self.led_set = {
                'onboard_led': self.settings.get('Wifi-config', 'onboard_led'), 
                'led_inverted': self.settings.get('Wifi-config', 'led_inverted')
                }
            self.testhost   = self.settings.get('MQTT-config', 'Broker')
            self.store_ip    = True
        
        elif not use_config_json:
            self.wlanSSID    = wlanSSID
            self.wlanPW      = wlanPW
            self.hostname    = hostname

            self.led_active  = use_onboard_led
            self.led_set = {
                'onboard_led': led_pin, 
                'led_inverted': led_inverted
                }
            self.testhost   = testhost
            self.loglevel   = loglevel
        self.max_attempts   = max_attempts
        self.is_pico        = sys.platform == 'rp2'
        self.led_onboard    = LedController(self.is_pico, self.led_set)
        self.led_onboard.set_active(self.led_active) # type: ignore
        Client.led_global = self.led_onboard

        # Ensure that wifi is ready
        self.led_flash(250, 250)
        self.led_flash(250, 250)
        self.led_flash(1000, 0)
        self.wlan = network.WLAN(network.STA_IF)

        # Pico-Check, probably obsolete!
        if self.is_pico:
            import rp2
            rp2.country = self.settings.get('Wifi-config', 'country')
            self.wlan.config(pm=0xa11140) 

        self.event = logger.Create('wifi', '/log/')

    def error_handler(self, errno):
        ERROR_CODES = {
            0: 'LINK_DOWN',
            1: 'LINK_JOIN',
            2: 'LINK_NOIP',
            3: 'LINK_UP',
            -1: 'LINK_FAIL',
            -2: 'LINK_NONET',
            -3: 'LINK_BADAUTH'
        }
        return ERROR_CODES.get(errno, f'{errno}: UNKNOWN_ERROR')
        
    def connect(self, timeout=3):
        max_attempts = self.max_attempts
        network.hostname(self.hostname)

        for attempts in range(1, max_attempts + 1):
            self.event.log('I', f'Connecting to {self.wlanSSID}... | Attempt: {attempts}/{max_attempts}')
            
            if self.wlan.isconnected():
                ifconf = self.wlan.ifconfig()
                self.event.log('I', f'Successfully reconnected to {self.wlanSSID}! IP={ifconf[0]}')
                self.led_onboard.on()
                return
            self.wlan.active(False)
            time.sleep(0.5)
            self.wlan.active(True)
            try:
                self.wlan.connect(self.wlanSSID, self.wlanPW)
            except OSError as E:
                self.event.log('F', f'OS-Error! - {E}. Will now reset...')
                time.sleep(1)
                machine.reset()

            if self.wait_connection(timeout=timeout):
                self.led_onboard.on()
                ifconfig = self.wlan.ifconfig()
                self.event.log('I',f'Connected successfully to {self.wlanSSID}. IP = {ifconfig[0]}')
                self.save_ip(ifconfig[0])
                return
            else:
                wstat = self.error_handler(self.wlan.status())
                self.event.log('W',f'Attempt {attempts}; Connection to {self.wlanSSID} failed! status={wstat}')

        self.event.log('E',f'Connection has been failed after Attempt {attempts}/{max_attempts}! Will now reset...')
        machine.reset()  

    def wait_connection(self, timeout=10):
        """
        Wait until WLAN is connected or timeout is reached.
        Returns True if connected.

        Parameters:
            timeout(int): The connection-timeout in seconds.
        """
        if self.wlan.isconnected():
            return True
        start = time.ticks_ms()
        
        while True:
            status = self.wlan.status()
            wstat = self.error_handler(self.wlan.status())

            if status == 0:  
                self.event.log('I', f'WSTAT: {wstat} - Wifi idle...')
            elif status == 1:
                self.event.log('I', f'WSTAT: {wstat} - Joining network...')
            elif status == -2:
                self.event.log('E', f'WSTAT: {wstat} - Network not found or bad signal!')
                return False
            elif status == -3:
                self.event.log('E', f'WSTAT: {wstat} - Authentication failed - Wrong password')
                return False
            elif status == 3:
                return True
            elif status == -1:
                self.event.log('E', f'WSTAT: {wstat} - Handshake with AP failed')
                return False
            self.led_flash(250, 500)
            self.led_flash(250, 0)

            if time.ticks_diff(time.ticks_ms(), start) > timeout * 1000:
                self.event.log('E', f'Timeout after {timeout}s waiting for connection')
                return False

            time.sleep(0.5)

    def save_ip(self, ip):
        if self.store_ip:
            self.settings.save_param('Wifi-config', 'IP', ip)
        else:
            pass

    def led_flash(self, on=1000, off=0):
        self.led_onboard.on()
        time.sleep_ms(on)
        self.led_onboard.off()
        time.sleep_ms(off)

    @classmethod
    def get_led(cls):
        if cls.led_global is None:
            raise RuntimeError('LED not initialized yet - Create Instance with client() first!')
        return cls.led_global
    
    def get_ifconfig(self):
        ifconfig = self.wlan.ifconfig()
        return ifconfig

    def check_connection(self, retries=5, timeout=5):
        """
        Parameters:
            retries (int): Number of retries. When reached, it logs an error and returns "False"
            timeout (int): Timeout for connection to the test host in s.
        """
        import socket
        testhost = self.testhost

        for trie in range (1, retries + 1):
            try:
                s = socket.socket()
                s.settimeout(timeout)
                s.connect(testhost)
                s.close()
                self.event.log('I', f'CONNTEST: Tested connection to {testhost} successfully!')
                return True
            except Exception as conn_error:
                self.event.log('E', f'{trie}/{retries}: Connection to {testhost} failed: {conn_error}')
        
        self.event.log('E', f'Connection to {testhost} was unsuccessful - {retries} attempts failed!')
        return False