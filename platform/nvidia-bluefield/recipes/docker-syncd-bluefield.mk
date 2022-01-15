#
# Copyright (c) 2019-2022 NVIDIA CORPORATION & AFFILIATES.
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

DOCKER_SYNCD_PLATFORM_CODE = bluefield

DOCKER_SYNCD_BASE_STEM = docker-syncd-$(DOCKER_SYNCD_PLATFORM_CODE)
DOCKER_SYNCD_BASE = $(DOCKER_SYNCD_BASE_STEM).gz
DOCKER_SYNCD_BASE_DBG = $(DOCKER_SYNCD_BASE_STEM)-$(DBG_IMAGE_MARK).gz

$(DOCKER_SYNCD_BASE)_PATH = $(PLATFORM_PATH)/docker-syncd-$(DOCKER_SYNCD_PLATFORM_CODE)
$(DOCKER_SYNCD_BASE)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)

$(DOCKER_SYNCD_BASE)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BULLSEYE)
$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_DEPENDS)
$(DOCKER_SYNCD_BASE)_DBG_IMAGE_PACKAGES = $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_IMAGE_PACKAGES)

SONIC_DOCKER_IMAGES += $(DOCKER_SYNCD_BASE)
SONIC_DOCKER_DBG_IMAGES += $(DOCKER_SYNCD_BASE_DBG)

ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_SYNCD_BASE)
endif

ifneq ($(ENABLE_SYNCD_RPC),y)
SONIC_INSTALL_DOCKER_DBG_IMAGES += $(DOCKER_SYNCD_BASE_DBG)
endif

$(DOCKER_SYNCD_BASE)_CONTAINER_NAME = syncd
$(DOCKER_SYNCD_BASE)_RUN_OPT += --privileged -t
$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/machine.conf:/etc/machine.conf
$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro

$(DOCKER_SYNCD_BASE)_DEPENDS += $(MFT)
$(DOCKER_SYNCD_BASE)_DBG_DEPENDS += $(LIBSWSSCOMMON_DBG)
               
$(DOCKER_SYNCD_BASE)_VERSION = 1.0.0
$(DOCKER_SYNCD_BASE)_PACKAGE_NAME = syncd

$(DOCKER_SYNCD_BASE)_RUN_OPT += -v /host/warmboot:/var/warmboot
