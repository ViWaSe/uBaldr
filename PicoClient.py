# MQTT Client Module
# There are 3 topics used, one for incoming order, one for configuration and one for the status from pico. config and status are for publishing messages.
# The Pico trys to establish the MQTT-Connection and assign to the Order-Topic. If successful, Pico publishs the "online"-message on status-topic. If it fails, Pico logs error and trys again.
# The incoming orders are processed and executed by order.py and the answer is published to the status-topic
# Settings stored in config.json

Version = '5.3.3'

import utime as time 
import order
from umqtt_simple import MQTTClient
from PicoWifi import led_onboard, check_status
from json_config_parser import config
from machine import Pin, Timer 
from logger import Log

# load settings from the config file
settings        = config('/params/config.json')
mqttClient      = settings.get('MQTT-config', 'Client')
mqttBroker      = settings.get('MQTT-config', 'Broker')
mqttPort        = settings.get('MQTT-config', 'Port')
mqttUser        = settings.get('MQTT-config', 'User')
mqttPW          = settings.get('MQTT-config', 'PW')
sensor_opt      = settings.get('Options', 'Sensor')
test_interval   = settings.get('MQTT-config', 'check_intervall')

# Create 3 MQTT-Topics for this device
topic_order    = str(mqttClient+'/order') # type: ignore
topic_status   = str(mqttClient+'/status') # type: ignore
topic_conf     = str(mqttClient+'/config') # type: ignore

# Create empty variables for client and for the led_toggle-function
client      = None
ledCount    = 0
last_msg    = time.time()
wd_counter  = 0
watchdog_last_chk = 0

# --------------------------- Sensor-Functions ---------------------------

# check, if sensor is installed
if sensor_opt == True:
    sensor_Pin  = settings.get('Sensor_settings','Input_Pin')
    # method      = settings.get('Sensor_settings','Method')
    db_timer    = settings.get('Sensor_settings','debouncing_period')
    in_message  = settings.get('Sensor_settings','message')

    sensor 		= Pin(sensor_Pin, Pin.IN, Pin.PULL_DOWN)

# Callback-function
def sensor_act(timer):
    client.publish(topic_status, in_message) # type: ignore

# Debouncing function
def debounce(pin):
    Timer().init(mode=Timer.ONE_SHOT, period=db_timer, callback=sensor_act) # type: ignore

# Get sensor value
if sensor_opt == True:
    sensor.irq(handler=debounce, trigger=Pin.IRQ_RISING)

# ----------------------- End of Sensor-Functions ------------------------ 

# Send config file as json-string
def send_json(file='config.json'):
    import json
    
    with open(file) as f:
        conf = json.load(f)
    content = json.dumps(conf)
    client.publish(topic_conf, content) # type: ignore

# MQTT Callback-Function:
def mqttDo(
        topic, 
        msg
        ):
    global client, topic_status, last_msg, wd_counter
    last_msg = time.time()
    nachricht = msg.decode('utf-8')
    wd_counter = 0
    if not nachricht:
        return False
    try:       
        ans = order.run(nachricht)
        if ans == None:
            pass
        elif ans == 'conn_lost':
            Log('MQTT', '[ FAIL  ]: MQTT-connection lost!')
            go()
        else:
            client.publish(topic_status, str(ans)) # type: ignore

    except Exception as Argument:
        Log('MQTT', '[ FAIL  ]: MQTT order failed! - ' + str(Argument))
        client.publish(topic_status, str(Argument)) # type: ignore
    return True

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
    client.set_last_will(topic=topic_status, msg='{"msg": "offline"}', retain=True)
    client.connect()
    Log('MQTT', '[ INFO  ]: MQTT connection established!')
    return client

# Watchdog process
def watchdog(watch_time=1800, cooldown = 5):
    global last_msg, wd_counter, watchdog_last_chk
    pico_time = time.time()
    
    # Avoid triggering watchdog too frequently
    if watchdog_last_chk == 0:  
        watchdog_last_chk = pico_time  # Set time and allow first check
    if pico_time - watchdog_last_chk < cooldown:
        return True 
    
    if pico_time - last_msg > watch_time:
        wd_counter += 1
        Log('Watchdog', '[ CHECK ]: Very quite here. Checking connection...')
        Log('Watchdog', '[ INFO  ]: RTC-Time='+str(pico_time)+' | Last msg='+str(last_msg))
        last_msg = pico_time
        watchdog_last_chk = pico_time
        client.publish(     # type: ignore
                topic_status, 
                'watchdog', 
                retain=False
                )
        # trigger a wifi-check only every 2nd call and if still no message recieved
        if wd_counter % 2 == 0:
            Log('Watchdog', '[ CHECK ]: No Message recieved. Checking network...')
            wifi_stat = check_status()
            if not wifi_stat:
                Log('Watchdog', '[ FAIL  ]: No Connection to Wifi. See Wifi.log for details!')
                return False
    return True


# Function for Onboard-LED as ok indicator and check connection
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

            client.subscribe(topic=recv_topic)
            client.publish(
                send_topic, 
                'online', 
                retain=True
                )
            
            # Wait for messages
            while True:
                led_toggle()
                client.check_msg()
                watchdog()
        
        except Exception as Argument:
            Log('MQTT', '[ FAIL  ]: MQTT connection failed! - ' + str(Argument))
            for i in range (4):
                led_onboard.on()
                time.sleep_ms(200)
                led_onboard.off()
                time.sleep_ms(200)
    