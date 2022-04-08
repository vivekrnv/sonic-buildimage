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

# sonic nvidia-bluefield installer image

SONIC_BF2_IMAGE_BASE = sonic-nvidia-bluefield
$(SONIC_BF2_IMAGE_BASE)_MACHINE = nvidia-bluefield

$(SONIC_BF2_IMAGE_BASE)_DEPENDS += $(MLXBF_BOOTCTL_DEB) \
                                   $(BOOTIMAGES) \
                                   $(MLNX_BLUEFIELD_BUILD_SCRIPTS)

# Install the packages during the build_debian phase
$(SONIC_BF2_IMAGE_BASE)_INSTALLS += $(ETHTOOL) \
                                    $(SYSTEMD_SONIC_GENERATOR) \
                                    $(LIBPKA_DEB) \
                                    $(KERNEL_MFT) \
                                    $(MFT_OEM) \
                                    $(MFT) \
                                    $(BOOTIMAGES) \
                                    $(MLXBF_BOOTCTL_DEB) \
                                    $(MLNX_BLUEFIELD_BUILD_SCRIPTS) \
                                    $(MLX_OPENIPMI_DEB) \
                                    $(MLX_OPENIPMI_SERVER_DEB) \
                                    $(BF2_PLATFORM_MODULE)

$(SONIC_BF2_IMAGE_BASE)_DOCKERS = $(SONIC_INSTALL_DOCKER_IMAGES)

# A compressed archive which contains individual files required for PXE boot
# A BFB image is also generated as a by-product of PXE image generation
SONIC_BF2_IMAGE_PXE = $(SONIC_BF2_IMAGE_BASE).tar.gz
$(SONIC_BF2_IMAGE_PXE)_IMAGE_TYPE = pxe
$(SONIC_BF2_IMAGE_PXE)_MACHINE = $($(SONIC_BF2_IMAGE_BASE)_MACHINE)
$(SONIC_BF2_IMAGE_PXE)_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_INSTALLS)
$(SONIC_BF2_IMAGE_PXE)_DEPENDS += $($(SONIC_BF2_IMAGE_BASE)_DEPENDS)
$(SONIC_BF2_IMAGE_PXE)_DOCKERS += $($(SONIC_BF2_IMAGE_BASE)_DOCKERS)
$(SONIC_BF2_IMAGE_PXE)_LAZY_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_LAZY_INSTALLS)
$(SONIC_BF2_IMAGE_PXE)_FILES += $(UPDATE_CAP) $(MLX_BOOTCTL_DRIVER)

# The traditional *.bin image. Works for sonic-sonic upgrade.
SONIC_BF2_IMAGE_BIN = $(SONIC_BF2_IMAGE_BASE).bin
$(SONIC_BF2_IMAGE_BIN)_IMAGE_TYPE = s2s # sonic-sonic only
$(SONIC_BF2_IMAGE_BIN)_MACHINE = $($(SONIC_BF2_IMAGE_BASE)_MACHINE)
$(SONIC_BF2_IMAGE_BIN)_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_INSTALLS)
$(SONIC_BF2_IMAGE_BIN)_DEPENDS += $($(SONIC_BF2_IMAGE_BASE)_DEPENDS)
$(SONIC_BF2_IMAGE_BIN)_DOCKERS += $($(SONIC_BF2_IMAGE_BASE)_DOCKERS)
$(SONIC_BF2_IMAGE_BIN)_LAZY_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_LAZY_INSTALLS)

# BFB (Bluefield BootStream) style image
SONIC_BF2_IMAGE_BFB = $(SONIC_BF2_IMAGE_BASE).bfb
$(SONIC_BF2_IMAGE_BFB)_IMAGE_TYPE = bfb
$(SONIC_BF2_IMAGE_BFB)_MACHINE = $($(SONIC_BF2_IMAGE_BASE)_MACHINE)
$(SONIC_BF2_IMAGE_BFB)_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_INSTALLS)
$(SONIC_BF2_IMAGE_BFB)_DEPENDS += $($(SONIC_BF2_IMAGE_BASE)_DEPENDS)
$(SONIC_BF2_IMAGE_BFB)_DOCKERS += $($(SONIC_BF2_IMAGE_BASE)_DOCKERS)
$(SONIC_BF2_IMAGE_BFB)_LAZY_INSTALLS += $($(SONIC_BF2_IMAGE_BASE)_LAZY_INSTALLS)
$(SONIC_BF2_IMAGE_BFB)_FILES += $(UPDATE_CAP) $(MLX_BOOTCTL_DRIVER)

SONIC_INSTALLERS += $(SONIC_BF2_IMAGE_PXE) $(SONIC_BF2_IMAGE_BIN) $(SONIC_BF2_IMAGE_BFB)
