#
# Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES.
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
import pytest
import sys

from unittest.mock import patch
from unittest.mock import mock_open
from unittest.mock import MagicMock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.chassis import Chassis
from sonic_platform.eeprom import Eeprom

from .test_chassis import platform_sample


vpd_sample = """

  VPD-KEYWORD    DESCRIPTION             VALUE
  -----------    -----------             -----
Read Only Section:

  PN             Part Number             MBF2H536C-CESOT
  EC             Revision                A5
  V2             N/A                     MBF2H536C-CESOT
  SN             Serial Number           MT2152X03653
  V3             N/A                     144d28a86368ec11800008c0ebe14b94
  VA             N/A                     MLX:MN=MLNX:CSKU=V2:UUID=V3:PCI=V0:MODL=BF2H536C
  V0             Misc Info               PCIeGen4 x16
  RV             Checksum Complement     0x7a
  IDTAG          Board Id                BlueField-2 DPU 100GbE Dual-Port QSFP56, integrated BMC, Secure Boot Enabled, Crypto Disabled, 32GB on-board DDR, 1GbE OOB management, FHHL
"""


fwinfo_sample = """
Querying Mellanox devices firmware ...

Device #1:
----------

  Device Type:      BlueField2
  Part Number:      MBF2H536C-CESO_Ax
  Description:      BlueField-2 P-Series DPU 100GbE Dual-Port QSFP56; integrated BMC; PCIe Gen4 x16; Secure Boot Enabled; Crypto Disabled; 32GB on-board DDR; 1GbE OOB management; FHHL
  PSID:             MT_0000000767
  PCI Device Name:  /dev/mst/mt41686_pciconf0
  Base GUID:        08c0eb0300e14b94
  Base MAC:         08c0ebe14b94
  Versions:         Current        Available
     FW             24.99.0932     N/A

  Status:           No matching image found

"""

@patch('sonic_py_common.device_info.get_platform', MagicMock(return_value=""))
@patch('sonic_py_common.device_info.get_path_to_platform_dir', MagicMock(return_value=""))
@patch('builtins.open', new_callable=mock_open, read_data=platform_sample)
@patch('os.path.isfile', MagicMock(return_value=True))
class TestEeprom:

    @patch('sonic_platform.eeprom.Vpd._read_raw', MagicMock(return_value=vpd_sample.split('\n')))
    def test_vpd(self, *args):
        eeprom = Eeprom()
        assert eeprom.get_serial_number() == "MT2152X03653"
        assert eeprom.get_product_name() == "BlueField-2 DPU 100GbE Dual-Port QSFP56, integrated BMC, Secure Boot Enabled, Crypto Disabled, 32GB on-board DDR, 1GbE OOB management, FHHL"
        assert eeprom.get_part_number() == "MBF2H536C-CESOT"
        assert eeprom.get_revision() == "A5"

        chassis = Chassis()
        assert chassis.get_serial() == "MT2152X03653"
        assert chassis.get_name() == "BlueField-2 DPU 100GbE Dual-Port QSFP56, integrated BMC, Secure Boot Enabled, Crypto Disabled, 32GB on-board DDR, 1GbE OOB management, FHHL"
        assert chassis.get_model() == "MBF2H536C-CESOT"
        assert chassis.get_revision() == "A5"

    @patch('sonic_platform.eeprom.FwManager._read_fw_info_raw', MagicMock(return_value=fwinfo_sample.split('\n')))
    def test_fwinfo(self, *args):
        eeprom = Eeprom()
        assert eeprom.get_base_mac() == "08:c0:eb:e1:4b:94"

        chassis = Chassis()
        assert chassis.get_base_mac() == "08:c0:eb:e1:4b:94"
