import json

with open('config.json', 'r') as f:
        File = json.load(f)

WLAN = File['Wifi-config']
wlan2 = WLAN[0]
SSID=wlan2['wlanSSID']

print(SSID)