# Smarthome Befehls-Modul @ vwall
Version = '4.1.2'
# 20.08.23

import LightControl, json
from PicoWifi import Log

# WLAN-Konfiguration
with open('config.json') as f:
    config = json.load(f)

def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f)

def saveIP(ip):
    config['Pico-IP'] = str(ip)
    save_config()

def getPara2(string):
    payload=string.split('_')
    if len(payload) == 4:
        output = payload[3]
    else:
        output = 'null'
    return output

def getPara(string):
    payload=string.split('_')
    return(payload[2])

def getPayload(string):
    payload=string.split('_')
    return(payload[1])

def getCommand(string):
    payload=string.split('_')
    return(payload[0])

def createList(string):
    raw=string.split(',')
    data=[]
    data.append(int(raw[0]))
    data.append(int(raw[1]))
    data.append(int(raw[2]))
    data.append(int(raw[3]))
    return data

def getRange(string):
    raw=string.split(',')
    data=[]
    data.append(int(raw[0]))
    data.append(int(raw[1]))
    return data

def getSetting(parameter, payload):
    if parameter == 'rgb':
        rgb = hex_to_rgb(payload)
        value = rgb
    elif parameter == 'rgbw':
        colour = createList(payload)
        value = colour
    return value

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  return tuple(rgb)

# Befehle:
# string-format: command_payload_parameter_parameter2

def action(order):
    command = getCommand(order)
    payload = getPayload(order)
    parameter = getPara(order)
    parameter2 = getPara2(order)
    if command == 'line':
        value = getSetting(parameter, payload)
        speed = getPara2(order)
        LightControl.line(value, int(speed))
    elif command == 'swap':
        value = getSetting(parameter, payload)
        speed = getPara2(order)
    elif command == 'single':
        value = getSetting(parameter, payload)
        segment=int(parameter2)
        LightControl.single(value, segment)       
    elif command == 'dim':
        LightControl.set_ramp(int(payload), int(parameter))
    elif command == 'clear':
        LightControl.clear()  

    elif command == 'range':
        Range = getRange(parameter2)
        value = getSetting(parameter, payload)
        start=Range[0]
        end=Range[1]
        colour = createList(payload)
        LightControl.Range(colour, start, end)
    elif command == 'chAnz':
        config['led_anzahl'] = int(payload)
        save_config()
        Log('Light Control: LED-Anzahl geändert! - Neu: ' + str(payload))
    elif command == 'chTopic':
        config['PiTopic'] = payload
        save_config()
        Log('Light Control: MQTT-Topic geändert! - Neu: ' + str(payload))
    elif command == 'chPin':
        config['led_out_1'] = int(payload)
        save_config()
        Log('Light Control: LED-Pin geändert! - Neu: ' + str(payload))
    elif command == 'autostart':
        if payload == 'true':
            config['start_power_on'] = True
            save_config()
            Log('Autostart aktiviert!')
        elif payload == 'false':
            config['start_power_on'] = False
            save_config()
            Log('Autostart deaktiviert!')
    elif command == 'xmas':
        LightControl.xmas_special()
    elif command == 'servo':
        import servo270 as servo
        servo.set(int(payload))
    else:
        pass