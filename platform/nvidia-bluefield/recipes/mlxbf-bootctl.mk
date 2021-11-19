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

MLXBF_BOOTCTL_DRIVER_VERSION = 2.1
MLXBF_BOOTCTL_DEB = mlxbf-bootctl_${MLXBF_BOOTCTL_DRIVER_VERSION}_${CONFIGURED_ARCH}.deb

$(MLXBF_BOOTCTL_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-bootctl
$(MLXBF_BOOTCTL_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_DEBS += $(MLXBF_BOOTCTL_DEB)

export MLXBF_BOOTCTL_DRIVER_VERSION
export MLXBF_BOOTCTL_DEB
