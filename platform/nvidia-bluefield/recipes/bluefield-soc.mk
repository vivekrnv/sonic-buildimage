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
BSD_VER = 4.0.2
BSD_REV = 12679
BFB_IMG_TYPE = prod

BSD_BASE_URL = https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/
BSD_BASE_SOURCE_URL = $(BSD_BASE_URL)/extras/SOURCES/

export BSD_VER BSD_REV BSD_BASE_SOURCE_URL BFB_IMG_TYPE

BF2_PLATFORM_DRIVERS =

TMFIFO_DRIVER_VERSION = 1.6
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

MLXBF2_GPIO_DRIVER_VERSION = 1.0
MLXBF2_GPIO_DRIVER = gpio-mlxbf2.ko
$(MLXBF2_GPIO_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/gpio-mlxbf2
$(MLXBF2_GPIO_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF2_GPIO_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF2_GPIO_DRIVER)
export MLXBF2_GPIO_DRIVER_VERSION MLXBF2_GPIO_DRIVER

MLXBF_I2C_DRIVER_VERSION = 1.0
MLXBF_I2C_DRIVER = i2c-mlxbf.ko
$(MLXBF_I2C_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/i2c-mlxbf
$(MLXBF_I2C_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_I2C_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_I2C_DRIVER)
export MLXBF_I2C_DRIVER_VERSION MLXBF_I2C_DRIVER

BLUEFIELD_EDAC_DRIVER_VERSION = 1.0
BLUEFIELD_EDAC_DRIVER = bluefield_edac.ko
$(BLUEFIELD_EDAC_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/bluefield_edac
$(BLUEFIELD_EDAC_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(BLUEFIELD_EDAC_DRIVER)
BF2_PLATFORM_DRIVERS += $(BLUEFIELD_EDAC_DRIVER)
export BLUEFIELD_EDAC_DRIVER_VERSION BLUEFIELD_EDAC_DRIVER

IPMB_DEV_INT_DRIVER_VERSION = 1.0
IPMB_DEV_INT_DRIVER = ipmb-dev-int.ko
$(IPMB_DEV_INT_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/ipmb-dev-int
$(IPMB_DEV_INT_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(IPMB_DEV_INT_DRIVER)
BF2_PLATFORM_DRIVERS += $(IPMB_DEV_INT_DRIVER)
export IPMB_DEV_INT_DRIVER_VERSION IPMB_DEV_INT_DRIVER

IPMB_HOST_DRIVER_VERSION = 0.1
IPMB_HOST_DRIVER = ipmb-host.ko
$(IPMB_HOST_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/ipmb-host
$(IPMB_HOST_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(IPMB_HOST_DRIVER)
BF2_PLATFORM_DRIVERS += $(IPMB_HOST_DRIVER)
export IPMB_HOST_DRIVER_VERSION IPMB_HOST_DRIVER

MLX_BOOTCTL_DRIVER_VERSION = 1.6
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

MLX_TRIO_DRIVER_VERSION = 0.2
MLX_TRIO_DRIVER = mlx-trio.ko
$(MLX_TRIO_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlx-trio
$(MLX_TRIO_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLX_TRIO_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLX_TRIO_DRIVER)
export MLX_TRIO_DRIVER_VERSION MLX_TRIO_DRIVER

MLXBF_BOOTCTL_DEB_VERSION = 2.1
MLXBF_BOOTCTL_DEB = mlxbf-bootctl_${MLXBF_BOOTCTL_DEB_VERSION}_${CONFIGURED_ARCH}.deb
$(MLXBF_BOOTCTL_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-bootctl

SONIC_MAKE_DEBS += $(MLXBF_BOOTCTL_DEB)
export MLXBF_BOOTCTL_DEB_VERSION MLXBF_BOOTCTL_DEB

MLXBF_LIVEFISH_DRIVER_VERSION = 1.0
MLXBF_LIVEFISH_DRIVER = mlxbf-livefish.ko
$(MLXBF_LIVEFISH_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-livefish
$(MLXBF_LIVEFISH_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_LIVEFISH_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_LIVEFISH_DRIVER)
export MLXBF_LIVEFISH_DRIVER_VERSION MLXBF_LIVEFISH_DRIVER

MLXBF_PMC_DRIVER_VERSION = 1.1
MLXBF_PMC_DRIVER = mlxbf-pmc.ko
$(MLXBF_PMC_DRIVER)_SRC_PATH = $(PLATFORM_PATH)/mlxbf-pmc
$(MLXBF_PMC_DRIVER)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

SONIC_MAKE_FILES += $(MLXBF_PMC_DRIVER)
BF2_PLATFORM_DRIVERS += $(MLXBF_PMC_DRIVER)
export MLXBF_PMC_DRIVER_VERSION MLXBF_PMC_DRIVER

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

ifeq ($(BFB_IMG_TYPE), prod)
BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)/bootimages/prod
BOOTIMAGES = mlxbf-bootimages-signed_$(BSD_VER)-$(BSD_REV)_arm64.deb
else
BOOTIMAGES_BASE_URL = $(BSD_BASE_URL)/bootimages/dev
BOOTIMAGES = mlxbf-bootimages-devsigned_$(BSD_VER)-$(BSD_REV)_arm64.deb
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
$(BF2_PLATFORM_MODULE)_PLATFORM = arm64-nvda_bf-mbf2m516a arm64-nvda_bf-mbf2h536c

$(BF2_PLATFORM_MODULE)_FILES = $(BF2_PLATFORM_DRIVERS)

SONIC_MAKE_DEBS += $(BF2_PLATFORM_MODULE)
export BF2_PLATFORM_MODULE_VERSION BF2_PLATFORM_MODULE BF2_PLATFORM_DRIVERS

MLX_OPENIPMI_DRIVER_VERSION = 2.0.25
MLX_OPENIPMI_DEB = mlx-libopenipmi0_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb
$(MLX_OPENIPMI_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlx-openipmi
$(MLX_OPENIPMI_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON) libsnmp-dev_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb
$(MLX_OPENIPMI_DEB)_RDEPENDS += $(MLNX_BLUEFIELD_BUILD_SCRIPTS)

MLX_OPENIPMI_SERVER_DEB = mlx-openipmi_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb
$(eval $(call add_derived_package,$(MLX_OPENIPMI_DEB),$(MLX_OPENIPMI_SERVER_DEB)))

SONIC_MAKE_DEBS += $(MLX_OPENIPMI_DEB)
export MLX_OPENIPMI_DRIVER_VERSION MLX_OPENIPMI_DEB MLX_OPENIPMI_SERVER_DEB
