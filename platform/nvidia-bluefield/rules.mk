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
BSD_VER=3.8.0
export BSD_VER


include $(PLATFORM_PATH)/$(RECIPE_DIR)/bfinstall.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/tmfifo.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlxbf-gige.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/gpio-mlxbf2.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/i2c-mlxbf.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/bluefield-edac.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/ipmb-dev-int.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/ipmb-host.mk
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
include $(PLATFORM_PATH)/$(RECIPE_DIR)/mlx-openipmi.mk
# include $(PLATFORM_PATH)/$(RECIPE_DIR)/libpka.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/docker-syncd-bluefield.mk
include $(PLATFORM_PATH)/$(RECIPE_DIR)/installer-image.mk

