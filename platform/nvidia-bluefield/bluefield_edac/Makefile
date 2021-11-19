#
# Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES.
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

BLUEFIELD_EDAC = bluefield_edac-${BLUEFIELD_EDAC_DRIVER_VERSION}
BLUEFIELD_EDAC_TAR = ${BLUEFIELD_EDAC}.tar.gz

$(addprefix $(DEST)/, $(BLUEFIELD_EDAC_DRIVER)): $(DEST)/% :
	rm -rf ${BLUEFIELD_EDAC} ${BLUEFIELD_EDAC_TAR} *.buildinfo *.changes *.deb
	wget -N "https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(BLUEFIELD_EDAC_TAR)"
	tar -z -f $(BLUEFIELD_EDAC_TAR) -x

	pushd ${BLUEFIELD_EDAC}

	# Build the package
ifeq ($(CROSS_BUILD_ENVIRON), y)
	CONFIG_SITE=/etc/dpkg-cross/cross-config.$(CONFIGURED_ARCH) LD_LIBRARY_PATH=$(CROSS_LIB_PATH) KVER=$(KVERSION) WITH_DKMS=0 dpkg-buildpackage -rfakeroot -us -uc -b -a$(CONFIGURED_ARCH) -Pcross,nocheck -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
else
	DEB_BUILD_OPTIONS=nocheck KVER=$(KVERSION) WITH_DKMS=0 dpkg-buildpackage -rfakeroot -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
endif

	mv $* $(DEST)/

	popd
