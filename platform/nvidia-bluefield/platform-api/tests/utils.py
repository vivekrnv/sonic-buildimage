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

platform_sample = """
{
    "chassis": {
        "name": "Nvidia-MBF2H516A",
        "components": [],
        "fans": [],
        "fan_drawers": [],
        "psus": [],
        "thermals": [],
        "sfps": [
            {
                "name": "p0"
            },
            {
                "name": "p1"
            }
        ]
    },
    "interfaces": {
        "Ethernet0": {
            "index": "1,1,1,1",
            "lanes": "0,1,2,3",
            "breakout_modes": {
                "1x100G": ["etp1"]
            }
        },
        "Ethernet4": {
            "index": "2,2,2,2",
            "lanes": "4,5,6,7",
            "breakout_modes": {
                "1x100G": ["etp2"]
            }
        }
    }
}
"""
