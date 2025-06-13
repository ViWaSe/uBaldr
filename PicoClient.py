# Pico Client: Connect PicoW to MQTT-Broker, assign to Topic and wait for messages

Version = '4.1.2'

import utime as time
import order, json
from umqtt_simple import MQTTClient
from PicoWifi import Log, led_onboard
from machine import Pin

# Konfiguration laden
with open('config.json') as f:
    config = json.load(f)
mqttClient=config['mqttClient']
mqttBroker=config['mqttBroker']
mqttPort=config['mqttPort']
mqttUser=config['mqttUser']
mqttPW=config['mqttPW']
Pitopic=config['PiTopic']
Alias=config['Alias']
md_pin=config['md_pin']

md = Pin(md_pin, Pin.IN, Pin.PULL_DOWN)
m_count = 1000

# Callback-Funktion:
def mqttDo(topic, msg):
    global Pitopic, client, Alias
    nachricht = msg.decode('utf-8')
    topic = topic.decode('utf-8')
    if nachricht == 'echo':
        client.publish(Alias, 'alive')
    elif nachricht == 'showStat':
        stat = showStat()
        client.publish(Alias, stat)
    else:
        order.action(nachricht)
        client.publish(Alias, 'OK')

# MQTT-Verbindung:    
def mqttConnect():
    global mqttClient, mqttBroker, mqttUser, mqttPW
    client = MQTTClient(mqttClient, mqttBroker, user=mqttUser, password=mqttPW)
    client.set_callback(mqttDo)
    client.connect()
    Log('MQTT: Connection established!')
    return client

client = mqttConnect()
ledCount = 0

# Funktion für Onboard-LED als Statusindikator:
def ledToggle():
    global ledCount
    ledCount +=1
    time.sleep_ms(1)
    if ledCount >=800:
        led_onboard.off()
        time.sleep_ms(100)
        led_onboard.on()
        ledCount = 0
    else:
        pass

def check_motion():
    global m_count
    md_value = md.value()
    if md_value == 1:
        if m_count >= 1000:
            client.publish(Alias, 'motion_detected')
            m_count = 0
        else:
            m_count += 1
            pass
    else:
        pass 

# Hauptprogramm:
def go():
    global Pitopic, client, Alias
    while True:
        try:
            led_onboard.on()
            time.sleep_ms(100)
            led_onboard.off()
            client.subscribe(topic=Pitopic)
            client.publish(Alias, 'online')
            
            # Warten auf Nachrichten
            while True:
                ledToggle()
                client.check_msg()
                check_motion()
        except Exception as Argument:
            Log('MQTT: ' + str(Argument))
            print('MQTT: ' + str(Argument))
            time.sleep(3)
            continue

def check_connection():
    pass