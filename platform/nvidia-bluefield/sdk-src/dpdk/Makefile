#
# Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES.
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

MAIN_TARGET = $(DPDK_HWS)
DERIVED_TARGETS = $(DPDK_HWS_DEV)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	
	rm -rf dpdk.hws/ dpdk.hws.zip

	# get sources
	wget $(DOCA_SDK_SOURCE_BASE_URL)/dpdk.hws.zip
	unzip dpdk.hws.zip
	pushd dpdk.hws/

	# Build the package
	# PATH variable is required for ninja to find the right version
	PATH=/usr/bin/:$(PATH) DPDK_CONFIG_OPTIONS='--cross-file ../config/arm/arm64_bluefield_linux_gcc' DEB_BUILD_OPTIONS='dpdk_config_options=-Dmachine=0xd08' dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)

	popd
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
