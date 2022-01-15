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
.SHELLFLAGS += -e

$(addprefix $(DEST)/, $(BF2_PLATFORM_MODULE)): $(DEST)/% :
	
	# Clean up
	rm -rf drivers/* \
		   cfg/bf2-modules.conf \
		   debian/platform-modules-bf2.postinst 

	mkdir -p drivers/
	mkdir -p cfg/

	$(foreach kernel_module, $(BF2_PLATFORM_DRIVERS), \
		cp $(PROJECT_ROOT)/$(FILES_PATH)/$(kernel_module) drivers/	
	)

	export driver_targets="$(BF2_PLATFORM_DRIVERS)"
	export kversion="$(KVERSION)"
	j2 templates/platform-modules-bf2.postinst.j2 > debian/platform-modules-bf2.postinst
	j2 templates/bf2-modules.conf.j2 > cfg/bf2-modules.conf
	
	chmod +x debian/platform-modules-bf2.postinst
	chmod 0644 cfg/bf2-modules.conf
	
# build package
ifeq ($(CROSS_BUILD_ENVIRON), y)
	CONFIG_SITE=/etc/dpkg-cross/cross-config.$(CONFIGURED_ARCH) LD_LIBRARY_PATH=$(CROSS_LIB_PATH) dpkg-buildpackage -rfakeroot -us -uc -b -a$(CONFIGURED_ARCH) -Pcross,nocheck -j$(SONIC_CONFIG_MAKE_JOBS)  
else
	DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -rfakeroot -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) 
endif

	mv ../$(BF2_PLATFORM_MODULE) $(DEST)/
