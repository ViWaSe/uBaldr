# Wifi network module for Prapberry pi pico and ESP-32
# configuration stored in JSON-File
# works with micropython v1.21.0 and higher
Version = '5.3.3'

import utime as time
import network, rp2, machine
from json_config_parser import config
from logger import Log

# Error-Log
wlan = network.WLAN(network.STA_IF)

# Get configuration
settings    = config('/params/config.json')
rp2.country = settings.get('Wifi-config', 'country')
wlanSSID    = settings.get('Wifi-config', 'SSID')
wlanPW      = settings.get('Wifi-config', 'PW')
wlanName    = settings.get('Wifi-config', 'Hostname')

led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# Handling of WLAN-Status-Codes
def error_handling(errorno):
    f0  = 'LINK_DOWN'       # No connection
    f1  = 'LINK_JOIN'       # try to connect
    f2  = 'LINK_NOIP'       # Connection successfull, but no IP config yet
    f3  = 'LINK_UP'         # Connection completely successfull
    f_1 = 'LINK_FAIL'       # connection aborted
    f_2 = 'LINK_NONET'      # SSID not found
    f_3 = 'LINK_BADAUTH'    # Authentification failed. Probably wrong password
    f_u = 'UNKNOWN_ERROR'   # If status code is not in the list
    errno = errorno
    if errno == 0:
        return f0
    elif errno == 1:
        return f1
    elif errno == 1:
        return f1
    elif errno == 2:
        return f2
    elif errno == 3:
        return f3
    elif errno == -1:
        return f_1
    elif errno == -2:
        return f_2
    elif errno == -3:
        return f_3
    else:
        return f_u

# Save IP-Adress in JSON-File
def saveIP(ip):
    settings.save_param('Wifi-config', 'IP', ip)

# Flash-Funktion of Onboard-LED
def led_flash(pause=1000):
    led_onboard.on()
    time.sleep_ms(pause)
    led_onboard.off()

# Connect to the Network
def connect():
    global wlan
    network.hostname(wlanName)
    wlan.config(pm = 0xa11140)
    if not wlan.isconnected():
        Log('WIFI', '[ INFO ]: Connecting to ' + str(wlanSSID) + '...')
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            wstat = error_handling(wlan.status())
            if wstat == 'LINK_UP' or wstat == 'LINK_NONET' or wstat == 'LINK_BADAUTH':
                if wstat == 'LINK_BADAUTH':
                    Log('WIFI', '[ FAIL ]: Wifi authentifaction failed! Probably wrong password!')
                break
            led_flash()
            time.sleep(1)
    if wlan.isconnected():
        led_onboard.on()
        Log('WIFI', '[ INFO ]: Connected!')
        w_status = wlan.ifconfig()
        Log('WIFI', '[ INFO ]: IP = ' + w_status[0] )
        saveIP(w_status[0])
    else:
        Log('WIFI', '[ FAIL ]: Connection failed! status: ' + str(wstat) + ' | try again...')
        led_onboard.off()
        connect()

# Check Wifi connection status. If not successful, try to reconnect.
def check_status():
    import socket
    global wlan
    try:
        addr = socket.getaddrinfo("google.com", 80)  # DNS-Auflösung testen
        Log('WIFI', '[ INFO ]: Successfully tested network connection!')
        return True
    except Exception as e:
        Log('WIFI', '[ FAIL ]: Wifi connection lost - ' + str(e))
        connect()  # Neu verbinden, wenn kein Internet da ist
        return False

