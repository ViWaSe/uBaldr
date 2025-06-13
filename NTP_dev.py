# NTP Timesetting
# Currently only used for Log-function
Version = '1.2'

import machine, json
import utime as time
import usocket as socket
import ustruct as struct

with open('time_setting.json') as f:
    config = json.load(f)
NTP_HOST=config['NTP_host']
GMT_winter=config['GMT_winter']
offline_time=config['offline_time']

def save_offline_time(tm):
    config['offline_time'] = tm
    with open('time_setting.json', 'w') as f:
        json.dump(config, f)


# Winterzeit / Sommerzeit
if GMT_winter == True:
    GMT_OFFSET = 3600 * 1 # 3600 = 1 h (Winterzeit)
else:
    GMT_OFFSET = 3600 * 2 # 3600 = 1 h (Sommerzeit)

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
    

