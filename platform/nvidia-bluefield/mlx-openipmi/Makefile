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

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -ex

MLX_OPENIPMI = mlx-OpenIPMI-${MLX_OPENIPMI_DRIVER_VERSION}
MLX_OPENIPMI_TAR = ${MLX_OPENIPMI}.tar.gz

MAIN_TARGET = $(MLX_OPENIPMI_DEB)
DERIVED_TARGETS = $(MLX_OPENIPMI_SERVER_DEB)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	rm -rf ${MLX_OPENIPMI} ${MLX_OPENIPMI_TAR} *.buildinfo *.changes *.deb
	wget -N "https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(MLX_OPENIPMI_TAR)"
	tar -z -f $(MLX_OPENIPMI_TAR) -x
	
	pushd ${MLX_OPENIPMI}

	# Build the package
ifeq ($(CROSS_BUILD_ENVIRON), y)	
	dpkg-buildpackage -rfakeroot -us -uc -b -d -a$(CONFIGURED_ARCH) -Pcross,nocheck -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
else
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -rfakeroot -us -uc -b -d -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
endif
	popd

	mv $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)