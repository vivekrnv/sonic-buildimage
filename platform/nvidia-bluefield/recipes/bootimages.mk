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

BOOTIMAGES_VERSION = 3.8.0-11969
BOOTIMAGES_BASE_PATH = $(PLATFORM_PATH)/sdk-src/sonic-bluefield-packages/bin/BlueField-$(BFINSTALL_VERSION)

BOOTIMAGES_BASE_URL =

BOOTIMAGES = mlxbf-bootimages_$(BFINSTALL_VERSION)_arm64.deb

ifneq ($(BOOTIMAGES_BASE_URL), )
$(BOOTIMAGES)_URL = $(BOOTIMAGES_BASE_URL)/$(BOOTIMAGES)
SONIC_ONLINE_DEBS += $(BOOTIMAGES)
else
$(BOOTIMAGES)_PATH = $(BOOTIMAGES_BASE_PATH)
SONIC_COPY_DEBS += $(BOOTIMAGES)
endif

export BOOTIMAGES