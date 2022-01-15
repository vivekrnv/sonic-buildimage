#
# Copyright (c) 2021-2022 NVIDIA CORPORATION & AFFILIATES.
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

# Mellanox Bluefield build scripts

MLNX_BLUEFIELD_BUILD_SCRIPTS_VERSION = 3.6

MLNX_BLUEFIELD_BUILD_SCRIPTS = mlxbf-scripts_$(MLNX_BLUEFIELD_BUILD_SCRIPTS_VERSION)_$(CONFIGURED_ARCH).deb

$(MLNX_BLUEFIELD_BUILD_SCRIPTS)_SRC_PATH = $(PLATFORM_PATH)/bfscripts
$(MLNX_BLUEFIELD_BUILD_SCRIPTS)_DEPENDS += $(MLXBF_BOOTCTL_DEB) $(BOOTIMAGES)

SONIC_DPKG_DEBS += $(MLNX_BLUEFIELD_BUILD_SCRIPTS)
