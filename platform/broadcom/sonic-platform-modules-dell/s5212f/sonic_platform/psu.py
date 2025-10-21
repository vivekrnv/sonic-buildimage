#!/usr/bin/env python

########################################################################
# DellEMC S5212F
#
# Module contains an implementation of SONiC Platform Base API and
# provides the PSUs' information which are available in the platform
#
########################################################################


try:
    from sonic_platform_base.psu_base import PsuBase
    from sonic_platform.ipmihelper import IpmiSensor, IpmiFru
    from sonic_platform.fan import Fan
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

switch_sku = {
  "0K6MG9":('AC', 'exhaust'),
  "0GKK8W":('AC', 'intake'),
  "0VK93C":('AC', 'exhaust'),
  "05JHDM":('AC', 'intake'),
  "0D72R7":('AC', 'exhaust'),
  "02PC9F":('AC', 'exhaust'),
  "0JM5DX":('AC', 'intake'),
  "0TPDP8":('AC', 'exhaust'),
  "0WND1V":('AC', 'exhaust'),
  "05672M":('DC', 'intake'),
  "0CJV4K":('DC', 'intake'),
  "0X41RN":('AC', 'exhaust'),
  "0Y3N82":('AC', 'intake'),
  "0W4CMG":('DC', 'exhaust'),
  "04T94Y":('DC', 'intake')
}

class Psu(PsuBase):
    """DellEMC Platform-specific PSU class"""

    # { PSU-ID: { Sensor-Name: Sensor-ID } }
    SENSOR_MAPPING = { 1: { "State": 0x31, "Current": 0x39,
                            "Power": 0x37, "Voltage": 0x38 },
                       2: { "State": 0x32, "Current": 0x3F,
                            "Power": 0x3D, "Voltage": 0x3E } }
    # ( PSU-ID: FRU-ID }
    FRU_MAPPING = { 1: 0, 2: 0 }

    def __init__(self, psu_index):
        PsuBase.__init__(self)
        # PSU is 1-based in DellEMC platforms
        self.index = psu_index + 1
        self.state_sensor = IpmiSensor(self.SENSOR_MAPPING[self.index]["State"],
                                       is_discrete=True)
        self.voltage_sensor = IpmiSensor(self.SENSOR_MAPPING[self.index]["Voltage"])
        self.current_sensor = IpmiSensor(self.SENSOR_MAPPING[self.index]["Current"])
        self.power_sensor = IpmiSensor(self.SENSOR_MAPPING[self.index]["Power"])
        self.fru = IpmiFru(self.FRU_MAPPING[self.index])

        self._fan_list.append(Fan(fan_index=self.index, psu_fan=True,
            dependency=self))

    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return "PSU{}".format(self.index)

    def get_presence(self):
        """
        Retrieves the presence of the Power Supply Unit (PSU)

        Returns:
            bool: True if PSU is present, False if not
        """
        presence = False
        is_valid, state = self.state_sensor.get_reading()
        if is_valid:
            if (state & 0b1) == 1:
                presence = True

        return presence

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
           A float number of current temperature in Celcius up to
           nearest thousandth of one degree celcius, e.g. 30.125
        """
        return 0.0

    def get_model(self):
        """
        Retrieves the part number of the PSU

        Returns:
            string: Part number of PSU
        """
        return self.fru.get_board_part_number()

    def get_serial(self):
        """
        Retrieves the serial number of the PSU

        Returns:
            string: Serial number of PSU
        """
        return self.fru.get_board_serial()

    def get_revision(self):
        """
        Retrives thehardware revision of the device
        Returns:
            String: revision value of device
        """
        serial = self.fru.get_board_serial()
        if serial != "NA" and len(serial) == 23:
            return serial[-3:]
        else:
            return "NA"

    def is_replaceable(self):
        """
        Indicate whether this PSU is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False

    def get_status(self):
        """
        Retrieves the operational status of the PSU

        Returns:
            bool: True if PSU is operating properly, False if not
        """
        status = False
        is_valid, state = self.state_sensor.get_reading()
        if is_valid:
            if (state == 0x01):
                status = True

        return status

    def get_voltage(self):
        """
        Retrieves current PSU voltage output

        Returns:
            A float number, the output voltage in volts,
            e.g. 12.1
        """
        return 0.0

    def get_current(self):
        """
        Retrieves present electric current supplied by PSU

        Returns:
            A float number, electric current in amperes,
            e.g. 15.4
        """
        return 0.0

    def get_power(self):
        """
        Retrieves current energy supplied by PSU

        Returns:
            A float number, the power in watts,
            e.g. 302.6
        """
        return 0.0

    def get_input_voltage(self):
        """
        Retrieves current PSU voltage input

        Returns:
            A float number, the input voltage in volts,
            e.g. 12.1
        """
        return 0.0

    def get_input_current(self):
        """
        Retrieves present electric current supplied to PSU

        Returns:
            A float number, electric current in amperes,
            e.g. 15.4
        """
        return 0.0

    def get_input_power(self):
        """
        Retrieves current energy supplied to PSU

        Returns:
            A float number, the power in watts,
            e.g. 302.6
        """
        return 0.0

    def get_powergood_status(self):
        """
        Retrieves the powergood status of PSU

        Returns:
            A boolean, True if PSU has stablized its output voltages and
            passed all its internal self-tests, False if not.
        """
        status = False
        is_valid, state = self.state_sensor.get_reading()
        if is_valid:
            if (state == 0x01):
                status = True

        return status

    def get_mfr_id(self):
        """
        Retrives the Manufacturer Id of PSU

        Returns:
            A string, the manunfacturer id.
        """
        return self.fru.get_board_mfr_id()

    def get_type(self):
        """
        Retrives the Power Type of PSU

        Returns :
            A string, PSU power type
        """
        board_product = self.fru.get_board_product()
        if board_product is not None :
            info =  board_product.split(',')
            if 'AC' in info : return 'AC'
            if 'DC' in info : return 'DC'
        return None

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        Returns:
            integer: The 1-based relative physical position in parent
            device or -1 if cannot determine the position
        """
        return self.index

    def get_voltage_low_threshold(self):
        """
        Retrieves the low threshold PSU voltage output
        Returns:
            A float number, the low threshold output voltage in volts,
            e.g. 12.1
        """
        return 0.0

    def get_voltage_high_threshold(self):
        """
        Returns PSU high threshold in Volts
        """
        return 0.0

    def get_maximum_supplied_power(self):
        """
        Retrieves the maximum supplied power by PSU
        Returns:
            A float number, the maximum power output in Watts.
            e.g. 1200.1
        """
        return float(750)

    def set_status_led(self, color):
        """
        Sets the state of the PSU status LED
        Args:
            color: A string representing the color with which to set the PSU status LED
                   Note: Only support green and off
        Returns:
            bool: True if status LED state is set successfully, False if not
        """
        # Hardware not supported
        return False
