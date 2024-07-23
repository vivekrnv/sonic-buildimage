#
# led_control.py
#
# Platform-specific LED control functionality for SONiC
#

try:
    from sonic_led.led_control_base import LedControlBase
    import os
    import time
    import syslog
    import sonic_platform.platform
    import sonic_platform.chassis
except ImportError as e:
    raise ImportError(str(e) + " - required module not found")

SWPLD1_DIR = "/sys/bus/i2c/devices/17-0032/"
MAX_7220H3_FAN_DRAWERS = 6
MAX_7220H3_FANS_PER_DRAWER = 2

def DBG_PRINT(str):
    syslog.openlog("nokia-led")
    syslog.syslog(syslog.LOG_INFO, str)
    syslog.closelog()


class LedControl(LedControlBase):
    """Platform specific LED control class"""

    # Constructor
    def __init__(self):
        self.chassis = sonic_platform.platform.Platform().get_chassis()
        self._initDefaultConfig()

    def _initDefaultConfig(self):
        # The fan tray leds and system led managed by new chassis class API
        # leaving only a couple other front panel leds to be done old style
        DBG_PRINT("starting system leds")
        self._initSystemLed()
        DBG_PRINT(" led done")

    def _read_sysfs_file(self, sysfs_file):
        # On successful read, returns the value read from given
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'

        if (not os.path.isfile(sysfs_file)):
            return rv
        try:
            with open(sysfs_file, 'r') as fd:
                rv = fd.read()
        except Exception as e:
            rv = 'ERR'

        rv = rv.rstrip('\r\n')
        rv = rv.lstrip(" ")
        return rv

    def _write_sysfs_file(self, sysfs_file, value):
        # On successful write, the value read will be written on
        # reg_name and on failure returns 'ERR'
        rv = 'ERR'

        if (not os.path.isfile(sysfs_file)):
            return rv
        try:
            with open(sysfs_file, 'w') as fd:
                rv = fd.write(str(value))
        except Exception as e:
            rv = 'ERR'

        return rv

    def _initSystemLed(self):
        # Front Panel System LEDs setting
        oldfan = 0xf    # 0=amber, 1=green
        oldpsu = 0xf    # 0=amber, 1=green

        # Write sys led
        status = self._write_sysfs_file(SWPLD1_DIR+"led_sys", "1")
        if status == "ERR":
            DBG_PRINT(" System LED NOT set correctly")
        else:
            DBG_PRINT(" System LED set O.K. ")

        # Timer loop to monitor and set front panel Status, Fan, and PSU LEDs
        while True:
            # Front Panel FAN Panel LED setting
            good_fan = 0
            for fan in self.chassis._fan_list:
                if fan.get_status() == True:
                    good_fan = good_fan + 1
            
            if (good_fan == MAX_7220H3_FAN_DRAWERS * MAX_7220H3_FANS_PER_DRAWER):
                if (os.path.isfile(SWPLD1_DIR+"led_fan")):
                    if oldfan != 0x1:
                        self._write_sysfs_file(SWPLD1_DIR+"led_fan", "1")
                        oldfan = 0x1
                else:
                    oldfan = 0xf
            else:
                if (os.path.isfile(SWPLD1_DIR+"led_fan")):
                    if oldfan != 0x0:
                        self._write_sysfs_file(SWPLD1_DIR+"led_fan", "2")
                        oldfan = 0x0
                else:
                    oldfan = 0xf

            time.sleep(6)

