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

MFT_VERSION = 4.23.0
MFT_REVISION = 102

export MFT_VERSION MFT_REVISION

MFT = mft_$(MFT_VERSION)-$(MFT_REVISION)_arm64.deb
$(MFT)_SRC_PATH = $(PLATFORM_PATH)/mft
SONIC_MAKE_DEBS += $(MFT)

ifeq ($(BLDENV), bullseye)
$(MFT)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

BUILD_ARCH = $(shell dpkg-architecture -qDEB_BUILD_ARCH)
KERNEL_MFT = kernel-mft-dkms-modules-$(KVERSION)_$(MFT_VERSION)_$(BUILD_ARCH).deb
$(eval $(call add_derived_package,$(MFT),$(KERNEL_MFT)))
endif

MFT_OEM = mft-oem_$(MFT_VERSION)-$(MFT_REVISION)_arm64.deb
$(eval $(call add_derived_package,$(MFT),$(MFT_OEM)))
