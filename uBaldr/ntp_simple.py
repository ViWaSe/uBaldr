# ntp_simple.py
Version = [3, 1, 0]

import time
import machine
import ntptime


class NTP:
    def __init__(
        self,
        use_json_config=True,
        time_setting_file='/params/time_setting.json',
        use_winter_time=False,
        GMT_offset=3600
    ):

        self.time_setting_file = time_setting_file
        self.use_json_config = use_json_config

        if use_json_config:
            from json_config_parser import config
            self.settings = config(time_setting_file, layers=1)

            self.GMT_offset = self.settings.get('GMT_offset') or GMT_offset
            self.use_winter_time = self.settings.get('use_winter_time') or use_winter_time
        else:
            self.settings = None
            self.GMT_offset = GMT_offset
            self.use_winter_time = use_winter_time

        if self.use_winter_time:
            self.GMT_offset += 3600

    # --------------------------------------------------

    def sync(self, timeout=2):
        """
        Sync via NTP and set RTC.
        Saves time to JSON on success.
        """

        try:
            ntptime.settime()
            time.sleep(timeout)
        except Exception as e:
            return False, f"NTP failed: {e}"

        t = time.time() + self.GMT_offset
        tm = time.localtime(t)

        if tm[0] < 2022:
            return False, "Invalid time after NTP sync"

        self._set_rtc(tm)
        self._save_backup(tm)

        return True, "RTC synced via NTP"

    # --------------------------------------------------

    def restore_from_backup(self):
        """
        Restore RTC from JSON backup if available.
        """

        if not self.settings:
            return False, "No JSON config available"

        tm = self.settings.get('offline_time')
        if not tm:
            return False, "No offline_time stored"

        if tm[0] < 2022:
            return False, "Stored offline_time invalid"

        self._set_rtc(tm)
        return True, "RTC restored from backup"

    # --------------------------------------------------

    def boot(self):
        """
        Try NTP first, fallback to JSON backup.
        """

        ok, msg = self.sync()
        if ok:
            return ok, msg

        ok, msg = self.restore_from_backup()
        if ok:
            return ok, msg

        return False, "No valid time source available"

    # --------------------------------------------------

    def now(self):
        tm = machine.RTC().datetime()
        return (
            f"{tm[0]}-{tm[1]:02d}-{tm[2]:02d}|"
            f"{tm[4]:02d}:{tm[5]:02d}:{tm[6]:02d}"
        )

    # --------------------------------------------------
    # internals

    def _set_rtc(self, tm):
        machine.RTC().datetime((
            tm[0],  # year
            tm[1],  # month
            tm[2],  # day
            tm[6],  # weekday
            tm[3],  # hour
            tm[4],  # minute
            tm[5],  # second
            0
        ))

    def _save_backup(self, tm):
        if self.settings:
            self.settings.save_param(param='offline_time', new_value=list(tm))
