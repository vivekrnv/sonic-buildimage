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

BLUEFIELD_EDAC_DRIVER_VERSION = 1.0
BLUEFIELD_EDAC_DRIVER = bluefield_edac.ko

$(BLUEFIELD_EDAC_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/bluefield_edac
$(BLUEFIELD_EDAC_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_FILES += $(BLUEFIELD_EDAC_DRIVER)

export BLUEFIELD_EDAC_DRIVER_VERSION
export BLUEFIELD_EDAC_DRIVER
