# Time setting via NTP-Server

Version = [2,1,0]

import machine
import utime as time
import usocket as socket
import ustruct as struct


class NTP:
    def __init__(
            self,
            use_json_config=True,
            time_setting_file='/params/time_setting.json',
            use_winter_time=False,
            host='pool.ntp.org',
            GMT_offset=3600
            ):
        
        """
        Parameters:
            use_config_json (bool): Use a JSON-File for the settings.
            time_setting_file (str): The full path of the JSON-File with the Settings.
            use_winter_time (bool): Set it to True if you use a winter-offset (UTC+2 like in germany).
            host (str): The NTP-Host.
            GMT_offset (int): Time-offset in s. Default is 3600 (UTC+1)
        """

        if use_json_config:
            from json_config_parser import config
            self.time_setting   = config(time_setting_file, layers=1)
            self.GMT_winter     = self.time_setting.get(param='use_winter_time')
            self.offline_time   = self.time_setting.get(param='offline_time') 
            self.host           = self.time_setting.get(param='NTP_host')
            self.GMT_offset     = self.time_setting.get(param='GMT_offset')
        else:
            self.GMT_winter     = use_winter_time
            self.host           = host
            self.GMT_offset     = GMT_offset
            self.offline_time   = [2025, 10, 11, 0, 0, 0]
    
    def setRTC(self):
        tm = self.get_time()
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

    def timestamp(self):
        try:
            self.setRTC()
        except:
            pass
        tm = machine.RTC().datetime()
        return str(tm[0])+'-'+str(tm[1])+'-'+str(tm[2])+'|'+str(tm[4])+':'+str(tm[5])+':'+str(tm[6])

    def get_time(self):
        NTP_DELTA = 2208988800
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        if not self.GMT_winter:
            GMT_OFFSET = 3600 * 2

        addr = socket.getaddrinfo(self.host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        
        t = time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)
        year = t [0]
        if year >= 2055:
            year -=30
        actual_time = (year,) + t[1:]

        return actual_time
    
    def save_time(self, time):
        self.time_setting.save_param('offline_time', time)

    def getTimeRTC(self):
        tm = machine.RTC().datetime()
        return tm

# Not used:
UTC_MAP = {
    'UTC': 0,
    'UTC+1': 3600,
    'UTC+2': 7200
}