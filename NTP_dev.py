# NTP Timesetting
# Currently only used for Log-function
Version = '1.2'

import machine, json
import utime as time
import usocket as socket
import ustruct as struct
from json_config_parser import config

time_setting    = config('time_settin.json')

NTP_HOST        = time_setting.status('NTP_host')
winter          = time_setting.status('use_winter_time')
offline_time    = time_setting.status('offline_time')
GMT_OFFSET      = time_setting.status('GMT_offset')

# Winterzeit / Sommerzeit (This part is german since the "summer- and wintertime" is only used in germany)
# GMT-offset = 1h (3600s), für Sommerzeit 2h (7200s)
if winter == False:
    GMT_OFFSET = GMT_OFFSET * 2 # (Winterzeit)
else:
    pass

def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)

def setTimeRTC():
    tm = getTimeNTP()
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

def timestamp():
    try:
        setTimeRTC()
        tm = machine.RTC().datetime()
        save_offline_time(tm)
    except:
        tm = offline_time
    return str(tm[0])+'-'+str(tm[1])+'-'+str(tm[2])+'|'+str(tm[4])+':'+str(tm[5])+':'+str(tm[6])
    

