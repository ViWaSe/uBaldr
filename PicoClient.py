# MQTT Client Module
# There are 3 topics used, one for incoming order, one for configuration and one for the status. config and status are for publishing messages.
# The Pico trys to establish the MQTT-Connection and assign to the Order-Topic. If successful, Pico publish the "online"-message on status-topic. If it fails, Pico logs the error and trys again.
# The incoming orders are processed and executed by order.py and the answer is published to the status-topic
# Settings stored in config.json

# !The Order module is not yet finished! Please use the older Version (5.0) without json-support instead!

Version = '5.1j'

import utime as time
import order
from umqtt_simple import MQTTClient
from PicoWifi import Log, led_onboard
from json_config_parser import config
from machine import Pin, Timer

# load settings from the config file
settings    = config('config.json')
mqttClient  = settings.get('MQTT-config', 'Client')
mqttBroker  = settings.get('MQTT-config', 'Broker')
mqttPort    = settings.get('MQTT-config', 'Port')
mqttUser    = settings.get('MQTT-config', 'User')
mqttPW      = settings.get('MQTT-config', 'PW')
sensor_opt  = settings.get('Options', 'Sensor')

# Create 3 MQTT-Topics for this device
topic_order    = str(mqttClient+'/order')
topic_status   = str(mqttClient+'/status')
topic_conf     = str(mqttClient+'/config')

# Create empty variables for client and for the led_toggle-function
client      = 0
ledCount    = 0

# --------------------------- Sensor-Functions ---------------------------

# check, if sensor is installed
if sensor_opt == True:
    sensor_Pin  = settings.get('Sensor_settings','Input_Pin')
    # method      = settings.get('Sensor_settings','Method')
    db_timer    = settings.get('Sensor_settings','debouncing_period')
    sensor 		= Pin(sensor_Pin, Pin.IN, Pin.PULL_DOWN)
    in_message  = settings.get('Sensor_settings','message')

# Callback-function
def sensor_act(timer):
    client.publish(topic_status, in_message)

# Debouncing function
def debounce(pin):
    Timer().init(mode=Timer.ONE_SHOT, period=db_timer, callback=sensor_act)

# Get sensor value
if sensor_opt == True:
    sensor.irq(handler=debounce, trigger=Pin.IRQ_RISING)

# -------------------------- /Sensor-Functions\ -------------------------- 

# Send config file as json-string
def send_json(file='config.json'):
    import json
    
    with open(file) as f:
        conf = json.load(f)
    content = json.dumps(conf)
    client.publish(topic_conf, content)

# MQTT Callback-Function:
def mqttDo(
        topic, 
        msg
        ):
    global client, topic_status
    nachricht = msg.decode('utf-8')
    try:       
        ans = order.proc(nachricht).run()
        
        if ans == 'lost':
            Log('MQTT-connection lost!')
            go()
        elif ans == 'send_config':
            send_json('config.json')
        else:
            client.publish(topic_status, ans)

    except Exception as Argument:
        Log('MQTT order failed! - ' + str(Argument))
        client.publish(topic_status, Argument)

# Function: Establish MQTT-Connection    
def mqttConnect(
        mqttClient=mqttClient, 
        mqttBroker=mqttBroker, 
        mqttUser=mqttUser, 
        mqttPW=mqttPW
        ):
    client = MQTTClient(
        mqttClient, 
        mqttBroker, 
        user=mqttUser, 
        password=mqttPW
        )
    client.set_callback(mqttDo)
    client.set_last_will(topic=topic_status, msg='offline', retain=True)
    client.connect()
    Log('MQTT connection established!')
    return client

# Function for Onboard-LED as ok indicator
def led_toggle(onTime=800):
    global ledCount
    ledCount +=1
    time.sleep_ms(1)
    if ledCount >= onTime:
        led_onboard.off()
        time.sleep_ms(100)
        led_onboard.on()
        ledCount = 0
    else:
        pass
    
# Main - just call go() to start the Loop
def go(
        recv_topic=topic_order, 
        send_topic=topic_status
        ):
    
    global client

    # Try to establish MQTT-Connection
    while True:
        try:
            client = mqttConnect()
            led_onboard.on()
            time.sleep_ms(100)
            led_onboard.off()

            client.subscribe(topic=recv_topic)
            client.publish(send_topic, 'online', retain=True)
            
            # Wait for messages
            while True:
                led_toggle()
                client.check_msg()
        
        except Exception as Argument:
            Log('MQTT connection failed! - ' + str(Argument))
            time.sleep(1)
            continue
    