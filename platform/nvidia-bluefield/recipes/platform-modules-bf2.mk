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

# Bluefield2 Platform Modules

BF2_PLATFORM_MODULE_VERSION = 1.0

export BF2_PLATFORM_MODULE_VERSION

BF2_PLATFORM_MODULE = platform-modules-bf2_$(BF2_PLATFORM_MODULE_VERSION)_arm64.deb
$(BF2_PLATFORM_MODULE)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-bf2

# Bluefield Drivers
BF2_PLATFORM_DRIVERS = $(MLXBF_GIGE_DRIVER) $(IPMB_HOST_DRIVER) $(MLXBF_I2C_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLX_TRIO_DRIVER) $(MLXBF_LIVEFISH_DRIVER) $(MLXBF_PMC_DRIVER)
BF2_PLATFORM_DRIVERS += $(TMFIFO_DRIVER) $(MLXBF2_GPIO_DRIVER) $(BLUEFIELD_EDAC_DRIVER)
BF2_PLATFORM_DRIVERS += $(IPMB_DEV_INT_DRIVER) $(MLXBF_PKA_DRIVER) $(MLX_BOOTCTL_DRIVER)

$(BF2_PLATFORM_MODULE)_FILES = $(BF2_PLATFORM_DRIVERS)
$(BF2_PLATFORM_MODULE)_PLATFORM = arm64-nvda_bf-mbf2m516a arm64-nvda_bf-mbf2h536c

SONIC_MAKE_DEBS += $(BF2_PLATFORM_MODULE)

export BF2_PLATFORM_MODULE
export BF2_PLATFORM_DRIVERS
