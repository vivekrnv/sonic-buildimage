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
    import re
    import os
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

MLXBF_BASE_PATH = '/sys/kernel/debug/mlxbf-ptm/monitors/status'

SENSORS = [
    {'name': 'CPU', 'mlxbf_sensor_name': 'core_temp', 'ht': 95, 'cht': 100},
    {'name': 'DDR', 'mlxbf_sensor_name': 'ddr_temp', 'ht': 95, 'cht': 100},
    {'name': 'SFP0', 'dev_index': '0'},
    {'name': 'SFP1', 'dev_index': '0.1'},
]

def get_mget_dev_prefix():
    mst_devices = os.listdir('/dev/mst')
    if not mst_devices:
        logger.log_error('/dev/mst is empty')
        return None
    m = re.match(r"^(.*)_pciconf", mst_devices[0])
    return m.group(1)

def initialize_chassis_thermals():
    thermal_list = []
    dev_prefix = get_mget_dev_prefix()
    for s in SENSORS:
        if 'dev_index' in s:
            s['dev_prefix'] = dev_prefix
        thermal_list.append(Thermal(**s))
    return thermal_list

def read_temp_mlxbf(sensor_name):
    path = f'{MLXBF_BASE_PATH}/{sensor_name}'
    try:
        with open(path) as f:
            return float(f.readline().strip())
    except Exception as e:
        logger.log_error(f'Failed to read {sensor_name} - {str(e)}')
        return 'N/A'

def mget_temp_read(dev_prefix, dev_index):
    path = f'/dev/mst/{dev_prefix}_pciconf{dev_index}'
    cmd = f'mget_temp -d {path}'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if err:
        logger.log_error(f'Failed to exec mget_temp - {err.decode()}')
        return 'N/A'
    value = output.decode().strip()
    return float(value)

class Thermal(ThermalBase):
    def __init__(self, name, mlxbf_sensor_name=None, dev_index=None, dev_prefix = None, ht='N/A', cht='N/A'):
        super(Thermal, self).__init__()
        self.name = name
        self.mlxbf_sensor_name = mlxbf_sensor_name
        self.dev_index = dev_index
        self.dev_prefix = dev_prefix
        self.ht = ht
        self.cht = cht

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

        if self.mlxbf_sensor_name:
            return read_temp_mlxbf(self.mlxbf_sensor_name)
        else:
            return mget_temp_read(self.dev_prefix, self.dev_index)

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return self.ht

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return self.cht

    def get_low_threshold(self):
        """
        Retrieves the low threshold temperature of thermal

        Returns:
            A float number, the low threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return 'N/A'

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold temperature of thermal

        Returns:
            A float number, the low critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return 'N/A'
