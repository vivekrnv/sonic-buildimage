#!/usr/bin/env python
#
# Name: thermal.py, version: 1.0
#
# Description: Module contains the definitions of SONiC platform APIs
#

try:
    import os
    import logging
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Thermal(ThermalBase):

    __core_temp_path = "/sys/devices/platform/coretemp.0/hwmon/hwmon1/temp{}_input"
    __switch_thermal_path = "/sys/devices/virtual/hwmon/hwmon1/temp{}_input"
    __max_temp_path = "/sys/devices/platform/coretemp.0/hwmon/hwmon1/temp{}_max"
    __name_of_thermal = [
        "Core 0 Temperature",
        "Core 1 Temperature",
        "Core 2 Temperature",
        "Core 3 Temperature",
        "Core 4 Temperature",
        "FrontSide Temperature",
        "FanBoard Temperature",
        "ASIC Temperature",
        "Center Temperature",
        "CPU Board Temperature",
        "Switch die temperature",
        "PSU1 Temperature1",
        "PSU2 Temperature1",
        "PSU1 Temperature2",
        "PSU2 Temperature2"
    ]
    __thermal_path_list = [
        __core_temp_path.format(1),
        __core_temp_path.format(2),
        __core_temp_path.format(3),
        __core_temp_path.format(4),
        __core_temp_path.format(5),
        __switch_thermal_path.format(1),
        __switch_thermal_path.format(2),
        __switch_thermal_path.format(3),
        __switch_thermal_path.format(4),
        __switch_thermal_path.format(5),
        __switch_thermal_path.format(6),
        __switch_thermal_path.format(7),
        __switch_thermal_path.format(8),
        __switch_thermal_path.format(9),
        __switch_thermal_path.format(10)
    ]
    __max_temp_path_list = [
        __max_temp_path.format(1),
        __max_temp_path.format(2),
        __max_temp_path.format(3),
        __max_temp_path.format(4),
        __max_temp_path.format(5),
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]

    def __init__(self, index):
        self.__index = index

        self.__thermal_temp_attr = self.__thermal_path_list[self.__index]
        self.__max_temp_attr = self.__max_temp_path_list[self.__index]

    def __get_attr_value(self, attr_path):

        retval = 'ERR'
        if not os.path.isfile(attr_path):
            return retval

        try:
            with open(attr_path, 'r') as fd:
                retval = fd.read()
        except FileNotFoundError:
            logging.error("File %s not found.  Aborting", attr_path)
        except (OSError, IOError) as ex:
            logging.error("Cannot open - %s: %s", attr_path, repr(ex))

        retval = retval.rstrip(' \t\n\r')
        return retval


##############################################
# Device methods
##############################################


    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return self.__name_of_thermal[self.__index]

    def get_presence(self):
        """
        Retrieves the presence of the device

        Returns:
            bool: True if device is present, False if not
        """
        attr_path = self.__thermal_temp_attr
        return os.path.isfile(attr_path)

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device

        Returns:
            string: Model/part number of device
        """
        raise NotImplementedError

    def get_serial(self):
        """
        Retrieves the serial number of the device

        Returns:
            string: Serial number of device
        """
        raise NotImplementedError

    def get_status(self):
        """
        Retrieves the operational status of the device

        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        status = False
        if self.get_presence():
            status = True

        return status

##############################################
# THERMAL methods
##############################################

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        attr_path = self.__thermal_temp_attr

        attr_rv = self.__get_attr_value(attr_path)
        if attr_rv != 'ERR':
            temperature = float(attr_rv) / 1000
        else:
            raise SyntaxError

        return temperature

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        attr_path = self.__max_temp_attr

        if attr_path == '':
            raise NotImplementedError
        else:
            attr_rv = self.__get_attr_value(attr_path)
            if attr_rv != 'ERR':
                high_threshold = float(attr_rv) / 1000
            else:
                raise SyntaxError

        return high_threshold

    def get_low_threshold(self):
        """
        Retrieves the low threshold temperature of thermal

        Returns:
            A float number, the low threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        raise NotImplementedError

    def set_high_threshold(self, temperature):
        """
        Sets the high threshold temperature of thermal

        Args :
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125

        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        raise NotImplementedError

    def set_low_threshold(self, temperature):
        """
        Sets the low threshold temperature of thermal

        Args :
            temperature: A float number up to nearest thousandth of one degree Celsius,
            e.g. 30.125

        Returns:
            A boolean, True if threshold is set successfully, False if not
        """
        raise NotImplementedError
