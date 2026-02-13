import machine
import time

# set frequency to 240MHz
machine.freq(240000000)

# Short break to stabilize
time.sleep_ms(100)

# Import LightControl
import LightControl

