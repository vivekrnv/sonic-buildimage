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

IPMB_HOST_DRIVER_VERSION = 0.1
IPMB_HOST_DRIVER = ipmb-host.ko

$(IPMB_HOST_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/ipmb-host
$(IPMB_HOST_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_FILES += $(IPMB_HOST_DRIVER)

export IPMB_HOST_DRIVER_VERSION
export IPMB_HOST_DRIVER
