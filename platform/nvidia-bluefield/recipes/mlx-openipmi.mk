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

MLX_OPENIPMI_DRIVER_VERSION = 2.0.25
MLX_OPENIPMI_DEB = mlx-libopenipmi0_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb
MLX_OPENIPMI_SERVER_DEB = mlx-openipmi_${MLX_OPENIPMI_DRIVER_VERSION}-3_arm64.deb


$(MLX_OPENIPMI_DEB)_SRC_PATH = $(PLATFORM_PATH)/mlx-openipmi
$(MLX_OPENIPMI_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON) libsnmp-dev_$(SNMPD_VERSION_FULL)_$(CONFIGURED_ARCH).deb
SONIC_MAKE_DEBS += $(MLX_OPENIPMI_DEB)
$(eval $(call add_derived_package,$(MLX_OPENIPMI_DEB),$(MLX_OPENIPMI_SERVER_DEB)))

export MLX_OPENIPMI_DRIVER_VERSION
export MLX_OPENIPMI_DEB
export MLX_OPENIPMI_SERVER_DEB
