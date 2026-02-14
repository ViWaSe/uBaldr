# uBaldr boot.py
# v1.0.1

import machine
import time
import sys

platform = sys.platform

if platform == 'esp32':
    # set frequency to 240MHz
    machine.freq(240000000)

# Short break to stabilize
time.sleep_ms(100)

# Import LightControl
import LightControl

