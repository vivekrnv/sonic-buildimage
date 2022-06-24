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

MAIN_TARGET = $(RDMA_CORE)
DERIVED_TARGETS = $(RDMA_CORE_DERIVED_DEBS)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	
	rm -rf rdma-core/ rdma-core.zip
	
	# get sources
	wget $(DOCA_SDK_SOURCE_URL)/rdma-core.zip
	unzip rdma-core.zip
	
	# build
	pushd rdma-core/
	patch -p1 < ../disable-ibverb-dependencies.patch

	find . -type f -exec touch {} +

	# Build the Debs
	PATH=/usr/bin/:$(PATH) dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)

	popd
	mv $(DERIVED_TARGETS) $* $(DEST)/

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
