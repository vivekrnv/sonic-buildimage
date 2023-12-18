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
#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the thermals data which are available in the platform
#
#############################################################################

try:
    from .device_data import BFVersion
    from .thermal_bf2 import initialize_chassis_thermals as bf2_init
    from .thermal_bf3 import initialize_chassis_thermals as bf3_init
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

def initialize_chassis_thermals(bfversion):
    if bfversion == BFVersion.BF2:
        return bf2_init()
    if bfversion == BFVersion.BF3:
        return bf3_init()
    raise Exception(f'Unexpected bf version - {bfversion}')