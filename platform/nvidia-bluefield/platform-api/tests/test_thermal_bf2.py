#
# Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES.
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

import os
import sys

from unittest.mock import patch
from unittest.mock import mock_open
from unittest.mock import MagicMock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.chassis import Chassis
from .utils import platform_sample


@patch('sonic_py_common.device_info.get_platform', MagicMock(return_value=""))
@patch('sonic_py_common.device_info.get_path_to_platform_dir', MagicMock(return_value=""))
@patch('builtins.open', new_callable=mock_open, read_data=platform_sample)
@patch('os.path.isfile', MagicMock(return_value=True))
class TestThermal:
    temp_test_mocked_vals = [123, 10.5, -1, None]

    def test_ipmi_mapping(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        thermal.ipmitool_get_sensor_field = MagicMock(return_value=10)
        assert thermal.ipmi_get_sensor_data('ASIC', 'invalid field') == None


    def test_chassis_thermal(self, *args):
        from sonic_platform.thermal_bf2 import SENSORS
        chassis = Chassis()
        thermal_list = chassis.get_all_thermals()
        assert thermal_list

        for s in SENSORS:
            assert 'name' in s
            assert 'ipminame' in s

        sensor_names = list(map(lambda x: x.get('name'), SENSORS))
        thermal_names = list(map(lambda x: x.get_name(), thermal_list))
        for sn in sensor_names:
            assert sn in thermal_names


    def test_get_temperature(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        from sonic_platform.thermal_bf2 import Thermal

        for tv in TestThermal.temp_test_mocked_vals:
            thermal.ipmitool_get_sensor_field = MagicMock(return_value=tv)
            t = Thermal('test', 'ipmi_test_sensor')
            assert t.get_temperature() == tv


    def test_get_high_threshold(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        from sonic_platform.thermal_bf2 import Thermal

        for tv in TestThermal.temp_test_mocked_vals:
            thermal.ipmitool_get_sensor_field = MagicMock(return_value=tv)
            t = Thermal('test', 'ipmi_test_sensor')
            assert t.get_high_threshold() is tv


    def test_get_high_critical_threshold(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        from sonic_platform.thermal_bf2 import Thermal

        for tv in TestThermal.temp_test_mocked_vals:
            thermal.ipmitool_get_sensor_field = MagicMock(return_value=tv)
            t = Thermal('test', 'ipmi_test_sensor')
            assert t.get_high_critical_threshold() is tv


    def test_get_low_threshold(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        from sonic_platform.thermal_bf2 import Thermal

        for tv in TestThermal.temp_test_mocked_vals:
            thermal.ipmitool_get_sensor_field = MagicMock(return_value=tv)
            t = Thermal('test', 'ipmi_test_sensor')
            assert t.get_low_threshold() is tv


    def test_get_low_critical_thresholdd(self, *args):
        from sonic_platform import thermal_bf2 as thermal
        from sonic_platform.thermal_bf2 import Thermal

        for tv in TestThermal.temp_test_mocked_vals:
            thermal.ipmitool_get_sensor_field = MagicMock(return_value=tv)
            t = Thermal('test', 'ipmi_test_sensor')
            assert t.get_low_critical_threshold() is tv
