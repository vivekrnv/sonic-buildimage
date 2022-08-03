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
if sys.version_info.major == 3:
    from unittest import mock
else:
    import mock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform import utils
from sonic_platform.chassis import Chassis
from sonic_platform.fan import Fan
from sonic_platform.fan_drawer import RealDrawer, VirtualDrawer
from sonic_platform.led import Led
from sonic_platform.psu import FixedPsu, Psu

class TestLed:
    @mock.patch('sonic_platform.led.Led._wait_files_ready', mock.MagicMock(return_value=True))
    @mock.patch('sonic_platform.chassis.extract_RJ45_ports_index', mock.MagicMock(return_value=True))
    def test_chassis_led(self):
        chassis = Chassis()
        assert chassis._led is None
        assert chassis.set_status_led('red') is False
        physical_led = chassis._led
        assert physical_led is not None
        self._verify_non_shared_led(physical_led, chassis)

    def _verify_non_shared_led(self, physical_led, obj):
        mock_file_content = self._mock_led_file_content(physical_led)

        def mock_read_str_from_file(file_path, **kwargs):
            return mock_file_content[file_path]

        def mock_write_file(file_path, content, **kwargs):
            mock_file_content[file_path] = content

        utils.read_str_from_file = mock_read_str_from_file
        utils.write_file = mock_write_file

        assert obj.get_status_led() == Led.STATUS_LED_COLOR_GREEN
        mock_file_content[physical_led.get_green_led_path()] = Led.LED_OFF
        assert obj.set_status_led(Led.STATUS_LED_COLOR_RED) is True
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_RED
        mock_file_content[physical_led.get_red_led_path()] = Led.LED_OFF
        assert obj.set_status_led(Led.STATUS_LED_COLOR_GREEN) is True
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_GREEN
        mock_file_content[physical_led.get_green_led_path()] = Led.LED_OFF
        assert obj.set_status_led(Led.STATUS_LED_COLOR_ORANGE) is True
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_RED
        mock_file_content[physical_led.get_orange_led_path()] = Led.LED_OFF

        assert obj.set_status_led(Led.STATUS_LED_COLOR_RED_BLINK)
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_RED_BLINK

        mock_file_content[physical_led.get_red_led_delay_off_path()] = Led.LED_OFF
        mock_file_content[physical_led.get_red_led_delay_on_path()] = Led.LED_OFF

        assert obj.set_status_led(Led.STATUS_LED_COLOR_GREEN_BLINK)
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_GREEN_BLINK
        mock_file_content[physical_led.get_green_led_delay_off_path()] = Led.LED_OFF
        mock_file_content[physical_led.get_green_led_delay_on_path()] = Led.LED_OFF

        assert obj.set_status_led(Led.STATUS_LED_COLOR_ORANGE_BLINK)
        assert obj.get_status_led() == Led.STATUS_LED_COLOR_RED_BLINK
        mock_file_content[physical_led.get_green_led_delay_off_path()] = Led.LED_OFF
        mock_file_content[physical_led.get_green_led_delay_on_path()] = Led.LED_OFF

    def _mock_led_file_content(self, led):
        return {
            led.get_green_led_path(): Led.LED_ON,
            led.get_red_led_path(): Led.LED_OFF,
            led.get_orange_led_path(): Led.LED_OFF,
            led.get_led_cap_path(): 'none green green_blink red red_blink orange',
            led.get_green_led_delay_off_path(): Led.LED_OFF,
            led.get_green_led_delay_on_path(): Led.LED_OFF,
            led.get_red_led_delay_off_path(): Led.LED_OFF,
            led.get_red_led_delay_on_path(): Led.LED_OFF,
            led.get_orange_led_delay_off_path(): Led.LED_OFF,
            led.get_orange_led_delay_on_path(): Led.LED_OFF,
        }

    @mock.patch('sonic_platform.led.Led._wait_files_ready', mock.MagicMock(return_value=True))
    def test_fan_led(self):
        fan_drawer = RealDrawer(0)
        self._verify_fan_led(fan_drawer)
        fan_drawer = VirtualDrawer(0)
        self._verify_fan_led(fan_drawer)

    def _verify_fan_led(self, fan_drawer):
        fan1 = Fan(0, fan_drawer, 1)
        fan2 = Fan(1, fan_drawer, 2)
        physical_led = fan_drawer.get_led()._led
        self._verify_shared_led(physical_led, fan1, fan2)

    def _verify_shared_led(self, physical_led, obj1, obj2):
        mock_file_content = self._mock_led_file_content(physical_led)

        def mock_read_str_from_file(file_path, **kwargs):
            return mock_file_content[file_path]

        def mock_write_file(file_path, content, **kwargs):
            mock_file_content[file_path] = content

        utils.read_str_from_file = mock_read_str_from_file
        utils.write_file = mock_write_file
        assert obj1.set_status_led(Led.STATUS_LED_COLOR_GREEN)
        assert obj2.get_status_led() == Led.STATUS_LED_COLOR_GREEN
        mock_file_content[physical_led.get_green_led_path()] = Led.LED_OFF
        assert obj2.set_status_led(Led.STATUS_LED_COLOR_RED)
        assert obj2.get_status_led() == Led.STATUS_LED_COLOR_RED
        assert obj1.set_status_led(Led.STATUS_LED_COLOR_RED)
        assert obj2.get_status_led() == Led.STATUS_LED_COLOR_RED

        mock_file_content[physical_led.get_red_led_path()] = Led.LED_OFF
        assert obj1.set_status_led(Led.STATUS_LED_COLOR_GREEN)
        assert obj1.get_status_led() == Led.STATUS_LED_COLOR_RED
        assert obj2.get_status_led() == Led.STATUS_LED_COLOR_RED
        assert obj2.set_status_led(Led.STATUS_LED_COLOR_GREEN)
        assert obj1.get_status_led() == Led.STATUS_LED_COLOR_GREEN
        assert obj1.get_status_led() == Led.STATUS_LED_COLOR_GREEN

    @mock.patch('sonic_platform.led.Led._wait_files_ready', mock.MagicMock(return_value=True))
    def test_psu_led(self):
        psu1 = Psu(0)
        psu2 = Psu(1)
        physical_led = Psu.get_shared_led()._led
        self._verify_shared_led(physical_led, psu1, psu2)

    @mock.patch('sonic_platform.led.Led._wait_files_ready', mock.MagicMock(return_value=True))
    def test_fixed_psu_led(self):
        psu = FixedPsu(0)
        physical_led = psu.led
        self._verify_non_shared_led(physical_led, psu)
