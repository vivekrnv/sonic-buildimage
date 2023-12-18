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

# Bluefied Software Distribution Version
BFSOC_VERSION = 4.5.0
BFSOC_REVISION = 12993
BFB_IMG_TYPE = prod

BSD_INTERNAL_BASE_URL = 
BSD_BASE_URL = 
BSD_BASE_SOURCE_URL = 

ifneq ($(BSD_INTERNAL_BASE_URL), )
BFSOC_FROM_INTERNAL = y
BSD_BASE_URL = $(BSD_INTERNAL_BASE_URL)
BSD_BASE_SOURCE_URL = $(BSD_BASE_URL)/build/install/distro/SRPMS/
DEV_BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)/build/install/distro/dev-release/DEBS/
PROD_BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)build/install/distro/ga-release/DEBS/
else
BFSOC_FROM_INTERNAL = n
BSD_BASE_URL = https://linux.mellanox.com/public/repo/bluefield/$(BFSOC_VERSION)-$(BFSOC_REVISION)/
BSD_BASE_SOURCE_URL = $(BSD_BASE_URL)/extras/SOURCES/
DEV_BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)/bootimages/dev/
PROD_BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)/bootimages/prod/
endif

export BFSOC_VERSION BFSOC_REVISION BSD_BASE_SOURCE_URL BFB_IMG_TYPE BFSOC_FROM_INTERNAL PLATFORM_PATH

BF2_PLATFORM_DRIVERS =

TMFIFO_DRIVER_VERSION = 1.7
TMFIFO_DRIVER = mlxbf-tmfifo.ko
$(TMFIFO_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/tmfifo
$(TMFIFO_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(TMFIFO_DRIVER)
BF2_PLATFORM_DRIVERS += $(TMFIFO_DRIVER)
export TMFIFO_DRIVER_VERSION TMFIFO_DRIVER

MLXBF_GIGE_DRIVER_VERSION = 1.1
MLXBF_GIGE_DRIVER = mlxbf-gige.ko
$(MLXBF_GIGE_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-gige
$(MLXBF_GIGE_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_GIGE_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_GIGE_DRIVER)
export MLXBF_GIGE_DRIVER_VERSION MLXBF_GIGE_DRIVER

# MLXBF3_GPIO_DRIVER_VERSION = 1.0
# MLXBF3_GPIO_DRIVER = gpio-mlxbf3.ko
# $(MLXBF3_GPIO_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/gpio-mlxbf3
# $(MLXBF3_GPIO_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

# SONIC_MAKE_FILES += $(MLXBF3_GPIO_DRIVER)
# BF2_PLATFORM_DRIVERS += $(MLXBF3_GPIO_DRIVER)
# export MLXBF3_GPIO_DRIVER_VERSION MLXBF3_GPIO_DRIVER

ifeq ($(BFSOC_VERSION), 4.2.0)
MLX_BOOTCTL_DRIVER_VERSION = 1.6
else
MLX_BOOTCTL_DRIVER_VERSION = 1.7
endif
MLX_BOOTCTL_DRIVER = mlx-bootctl.ko
$(MLX_BOOTCTL_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlx-bootctl
$(MLX_BOOTCTL_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLX_BOOTCTL_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLX_BOOTCTL_DRIVER)
export MLX_BOOTCTL_DRIVER_VERSION MLX_BOOTCTL_DRIVER

SDHCI_OF_DWCMSHC_DRIVER_VERSION = 1.0
SDHCI_OF_DWCMSHC_DRIVER = sdhci-of-dwcmshc.ko
$(SDHCI_OF_DWCMSHC_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/sdhci-of-dwcmshc
$(SDHCI_OF_DWCMSHC_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(SDHCI_OF_DWCMSHC_DRIVER)
BF2_PLATFORM_DRIVERS += $(SDHCI_OF_DWCMSHC_DRIVER)
export SDHCI_OF_DWCMSHC_DRIVER_VERSION SDHCI_OF_DWCMSHC_DRIVER

MLXBF_BOOTCTL_DEB_VERSION = 2.1
MLXBF_BOOTCTL_DEB = mlxbf-bootctl_${MLXBF_BOOTCTL_DEB_VERSION}_${CONFIGURED_ARCH}.deb
$(MLXBF_BOOTCTL_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-bootctl

SONIC_MAKE_DEBS += $(MLXBF_BOOTCTL_DEB)
export MLXBF_BOOTCTL_DEB_VERSION MLXBF_BOOTCTL_DEB

MLXBF_PKA_DRIVER_VERSION = 1.0
MLXBF_PKA_DRIVER = mlxbf-pka.ko
$(MLXBF_PKA_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-pka
$(MLXBF_PKA_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_PKA_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_PKA_DRIVER)
export MLXBF_PKA_DRIVER_VERSION MLXBF_PKA_DRIVER

PWR_MLXBF_DRIVER_VERSION = 1.0
PWR_MLXBF_DRIVER = pwr-mlxbf.ko
$(PWR_MLXBF_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/pwr-mlxbf
$(PWR_MLXBF_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(PWR_MLXBF_DRIVER)
BF2_PLATFORM_DRIVERS += $(PWR_MLXBF_DRIVER)
export PWR_MLXBF_DRIVER_VERSION PWR_MLXBF_DRIVER

RSHIM_DRIVER_VERSION = 2.0.6
RSHIM_DEB = rshim_${RSHIM_DRIVER_VERSION}-1_${CONFIGURED_ARCH}.deb
$(RSHIM_DEB)_SRC_PATH = $(PLATFORM_PATH)/rshim
$(RSHIM_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_DEBS += $(RSHIM_DEB)
export RSHIM_DRIVER_VERSION RSHIM_DEB

MLXBF_PTM_DRIVER_VERSION = 1.1
MLXBF_PTM_DRIVER = mlxbf-ptm.ko
$(MLXBF_PTM_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-ptm
$(MLXBF_PTM_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_PTM_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_PTM_DRIVER)
export MLXBF_PTM_DRIVER_VERSION MLXBF_PTM_DRIVER

ifeq ($(BFB_IMG_TYPE), prod)
BOOTIMAGES_BASE_URL = $(PROD_BOOTIMAGES_BASE_URL)
BOOTIMAGES = mlxbf-bootimages-signed_$(BFSOC_VERSION)-$(BFSOC_REVISION)_arm64.deb
else
BOOTIMAGES_BASE_URL = $(DEV_BOOTIMAGES_BASE_URL)
BOOTIMAGES = mlxbf-bootimages-devsigned_$(BFSOC_VERSION)-$(BFSOC_REVISION)_arm64.deb
endif

$(BOOTIMAGES)_URL = $(BOOTIMAGES_BASE_URL)/$(BOOTIMAGES)

SONIC_ONLINE_DEBS += $(BOOTIMAGES)
export BOOTIMAGES BOOTIMAGES_BASE_URL

MLNX_BLUEFIELD_BUILD_SCRIPTS_VERSION = 3.6
MLNX_BLUEFIELD_BUILD_SCRIPTS = mlxbf-scripts_$(MLNX_BLUEFIELD_BUILD_SCRIPTS_VERSION)_$(CONFIGURED_ARCH).deb
$(MLNX_BLUEFIELD_BUILD_SCRIPTS)_SRC_PATH = $(PLATFORM_PATH)/bfscripts
$(MLNX_BLUEFIELD_BUILD_SCRIPTS)_DEPENDS += $(MLXBF_BOOTCTL_DEB) $(BOOTIMAGES)
$(MLNX_BLUEFIELD_BUILD_SCRIPTS)_RDEPENDS += $(MLXBF_BOOTCTL_DEB) $(BOOTIMAGES)

SONIC_DPKG_DEBS += $(MLNX_BLUEFIELD_BUILD_SCRIPTS)
export MLNX_BLUEFIELD_BUILD_SCRIPTS

BF2_PLATFORM_MODULE_VERSION = 1.0
BF2_PLATFORM_MODULE = platform-modules-bf2_$(BF2_PLATFORM_MODULE_VERSION)_arm64.deb
$(BF2_PLATFORM_MODULE)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-bf2

$(BF2_PLATFORM_MODULE)_FILES = $(BF2_PLATFORM_DRIVERS)

SONIC_MAKE_DEBS += $(BF2_PLATFORM_MODULE)
export BF2_PLATFORM_MODULE_VERSION BF2_PLATFORM_MODULE BF2_PLATFORM_DRIVERS

MLX_OPENIPMI_DRIVER_VERSION = 2.0.25
MLX_OPENIPMI_DEB = mlx-libopenipmi0_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb
$(MLX_OPENIPMI_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlx-openipmi
$(MLX_OPENIPMI_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
$(MLX_OPENIPMI_DEB)_RDEPENDS += $(MLNX_BLUEFIELD_BUILD_SCRIPTS)

MLX_OPENIPMI_SERVER_DEB = mlx-openipmi_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb
$(eval $(call add_derived_package,$(MLX_OPENIPMI_DEB),$(MLX_OPENIPMI_SERVER_DEB)))

SONIC_MAKE_DEBS += $(MLX_OPENIPMI_DEB)
export MLX_OPENIPMI_DRIVER_VERSION MLX_OPENIPMI_DEB MLX_OPENIPMI_SERVER_DEB