#
# Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from sonic_py_common.logger import Logger
    import subprocess
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

THERMAL_TO_IPMI_MAPPING = {
    'temperature': 'Sensor Reading',
    'high_threshold': 'Upper non-critical',
    'high_critical_threshold': 'Upper critical',
    'low_threshold': 'Lower non-critical',
    'low_critical_threshold': 'Lower non-critical'
}

IPMI_PARAMS = {
    'user': 'ADMIN',
    'password': 'ADMIN',
    'port': 9001,
    'host': 'localhost',
    'interface': 'lan'
}

SENSORS = [
    {'name': 'ASIC', 'ipminame': 'bluefield'},
    {'name': 'DDR0_0', 'ipminame': 'ddr0_0'},
    {'name': 'DDR0_1', 'ipminame': 'ddr0_1'},
    {'name': 'DDR1_0', 'ipminame': 'ddr1_0'},
    {'name': 'DDR1_1', 'ipminame': 'ddr1_1'},
    {'name': 'SFP0', 'ipminame': 'p0'},
    {'name': 'SFP1', 'ipminame': 'p1'},
]

def ipmitool_get_sensor_field(sensor_name, sensor_data_field):
    cmd = f"ipmitool -U {IPMI_PARAMS['user']} -P {IPMI_PARAMS['password']} -p {IPMI_PARAMS['port']} -H {IPMI_PARAMS['host']} "\
          f"-I {IPMI_PARAMS['interface']} sdr get {sensor_name}_temp | grep '{sensor_data_field}'"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if err:
        logger.log_error('Failed to exec ipmitool')
        return 'N/A'
    value = output.decode().split(':')[1].strip()
    if value == 'No Reading':
        return 'N/A'
    return float(value.split()[0].strip())

def ipmi_get_sensor_data(sensor_name, sensor_data_field):
    if not sensor_data_field in THERMAL_TO_IPMI_MAPPING:
        logger.log_error('The sensor field {} is not present in THERMAL_TO_IPMI_MAPPING'.format(sensor_data_field))
        return None
    impi_field = THERMAL_TO_IPMI_MAPPING[sensor_data_field]
    return ipmitool_get_sensor_field(sensor_name, impi_field)

def initialize_chassis_thermals():
    thermal_list = []
    for s in SENSORS:
        thermal_list.append(Thermal(s['name'], s['ipminame']))
    return thermal_list

class Thermal(ThermalBase):
    def __init__(self, name, ipmi_name):
        super(Thermal, self).__init__()
        self.name = name
        self.ipmi_name = ipmi_name

    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return self.name

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        return ipmi_get_sensor_data(self.ipmi_name, 'temperature')

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return ipmi_get_sensor_data(self.ipmi_name, 'high_threshold')

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return ipmi_get_sensor_data(self.ipmi_name, 'high_critical_threshold')

    def get_low_threshold(self):
        """
        Retrieves the low threshold temperature of thermal

        Returns:
            A float number, the low threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return ipmi_get_sensor_data(self.ipmi_name, 'low_threshold')

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold temperature of thermal

        Returns:
            A float number, the low critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return ipmi_get_sensor_data(self.ipmi_name, 'low_critical_threshold')
