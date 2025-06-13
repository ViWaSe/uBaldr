# WLAN-Verbindungs-Modul V2.0 @ vwall
# Verbindungsdaten in config-Modul
Version = '4.1'

import utime as time
import network, rp2, machine
from json_config_parser import config

# Error-Log
LogCount = 100

def clearLog():
    global LogCount
    LogCount    = 100
    file        = open('Pico.log', 'w')
    file.write('***PicoW Log***' + '\n' + 'Version ' + Version + '\n')
    file.close()

def Log(issue):
    import NTP
    global LogCount
    time        = NTP.timestamp()
    LogCount    = LogCount - 1
    file        = open('Pico.log', 'a')
    file.write(str(time) + ' >>> ' + str(issue) + '\n')
    file.close()
    if LogCount < 1:
        clearLog()

# Konfiguration laden
settings    = config('config.json')
rp2.country = settings.get('Wifi-config', 'country')
wlanSSID    = settings.get('Wifi-config', 'SSID')
wlanPW      = settings.get('Wifi-config', 'PW')
LED         = settings.get('LightControl_settings', 'led_onboard')
led_onboard = machine.Pin(LED, machine.Pin.OUT, value=0)

def saveIP(ip):
    settings.save_param('Wifi-config', 'IP', ip)

def led_flash():
    led_onboard.on()
    time.sleep_ms(50)
    led_onboard.off()

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.config(pm = 0xa11140)
    if not wlan.isconnected():
        Log('Wifi: Connecting to ' + str(wlanSSID) + '...')
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < -1 or wlan.status() >= 3:
                break
            led_flash()
            time.sleep(1)
    if wlan.isconnected():
        led_onboard.on()
        Log('Wifi: Connected!')
        status = wlan.ifconfig()
        Log( 'Wifi: ip = ' + status[0] )
        saveIP(status[0])
    else:
        Log('Wifi: Connection failed! status: ' + str(wlan.status()) + ' | try again...')
        led_onboard.off()
        connect()



    