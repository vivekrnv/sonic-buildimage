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

IMAGE_TYPE=dev

BOOTIMAGES_BASE_URL = https://linux.mellanox.com/public/repo/bluefield/$(BSD_VER)/bootimages/$(IMAGE_TYPE)
BOOTIMAGES = mlxbf-bootimages_$(BSD_VER)-$(BSD_REV)_arm64.deb

# Required for building BFB image
UPDATE_CAP = update.cap

$(BOOTIMAGES)_URL = $(BOOTIMAGES_BASE_URL)/$(BOOTIMAGES)
SONIC_ONLINE_DEBS += $(BOOTIMAGES)

$(UPDATE_CAP)_URL = $(BOOTIMAGES_BASE_URL)/$(UPDATE_CAP)
SONIC_ONLINE_FILES += $(UPDATE_CAP)

export BOOTIMAGES UPDATE_CAP
