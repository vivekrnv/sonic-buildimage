#
# Copyright (c) 2016-2022 NVIDIA CORPORATION & AFFILIATES.
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

BFINSTALL_VERSION = 3.8.0.11969

BFINSTALL_BASE_URL = "http://fit69.mtl.labs.mlnx/auto/sw_mc_soc_release/BlueField-$(BFINSTALL_VERSION)"
BFINSTALL_FILE = BlueField-$(BFINSTALL_VERSION)_install.bfb
$(BFINSTALL_FILE)_URL = $(BFINSTALL_BASE_URL)/$(BFINSTALL_FILE)

SONIC_ONLINE_FILES += $(BFINSTALL_FILE)

export BFINSTALL_FILE
