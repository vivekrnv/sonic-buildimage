#
# Copyright (c) 2017-2022 NVIDIA CORPORATION & AFFILIATES.
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

RECIPE_DIR = recipes

# Bluefied Software Distribution Version
BSD_VER=3.8.5
BSD_REV=12027
BFB_IMG_TYPE=prod
export BSD_VER BSD_REV BFB_IMG_TYPE

override TARGET_BOOTLOADER=grub

include $(PLATFORM_PATH)/$(RECIPE_DIR)/bfinstall.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/tmfifo.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-gige.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/gpio-mlxbf2.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/i2c-mlxbf.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/bluefield-edac.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/ipmb-dev-int.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/ipmb-host.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlx-bootctl.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlx-trio.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-bootctl.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-livefish.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-pmc.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-pka.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/rshim.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/bootimages.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/bfscripts.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/platform-modules-bf2.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mft.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/dpu-sai.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlx-openipmi.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/sdk.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/platform-api.mk
# include $(PLATFORM_PATH)/$(RECIPE_DIR)/libpka.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/docker-syncd-bluefield.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/docker-syncd-bluefield-rpc.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/installer-image.mk

# Inject DPU sai into syncd
$(SYNCD)_DEPENDS += $(DPU_SAI)
$(SYNCD)_UNINSTALLS += $(DPU_SAI)

ifeq ($(ENABLE_SYNCD_RPC),y)
$(SYNCD)_DEPENDS := $(filter-out $(LIBTHRIFT_DEV),$($(SYNCD)_DEPENDS))
$(SYNCD)_DEPENDS += $(LIBSAITHRIFT_DEV) $(LIBTHRIFT_0_14_1_DEV)
endif

# Runtime dependency on DPU sai is set only for syncd
$(SYNCD)_RDEPENDS += $(DPU_SAI)

# Inject mft into platform monitor
$(DOCKER_PLATFORM_MONITOR)_DEPENDS += $(MFT)
