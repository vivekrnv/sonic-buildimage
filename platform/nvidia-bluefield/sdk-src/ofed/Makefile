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
BUILD_ARCH = $(shell dpkg-architecture -qDEB_BUILD_ARCH)

MAIN_TARGET = $(OFED_KERNEL)
DERIVED_TARGETS = $(OFED_DERIVED_DEBS)

OFED_TAR = MLNX_OFED_SRC-debian-$(OFED_VER_FULL).tgz
OFED_SRC = MLNX_OFED_SRC-$(OFED_VER_FULL)

SRC_DEB = mlnx-ofed-kernel-dkms_$(OFED_VER_SHORT)*_all.deb
SRC_DEB_DEPENDENCIES = mlnx-tools_*_$(BUILD_ARCH).deb \
		mlnx-ofed-kernel-utils_$(OFED_VER_SHORT)*_$(BUILD_ARCH).deb

DKMS_BMDEB = /var/lib/dkms/mlnx-ofed-kernel/$(OFED_KERNEL_VER_FULL)/bmdeb/
DKMS_TMP := $(shell mktemp -u -d -t dkms.XXXXXXXXXX)

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Make sure errors will be reported
	set -e

	sudo rm -rf MLNX_OFED_SRC*
	wget $(SDK_SOURCE_URL)/$(OFED_TAR)
	tar xf $(OFED_TAR)

	pushd $(OFED_SRC)/
	find . -type f -exec touch {} +

	sudo mv /bin/uname /bin/uname.orig
	cat << EOF >> /tmp/uname
	#!/bin/bash
	if [[ "\$$1" == "-r" ]]; then
		echo $(KVERSION)
		exit 0
	fi
	/bin/uname.orig \$$@
	EOF
	chmod +x /tmp/uname
	sudo mv /tmp/uname /bin/uname

	# Build the Debs
	sudo ./install.pl -k $(KVERSION) --kernel-only --build-only --without-depcheck --kernel-extra-args --force --with-mlnx-tools

	sudo chown -R ${USER} ./*

	pushd DEBS/*/aarch64/

	# put a lock here because dpkg does not allow installing packages in parallel
	while true; do
		if mkdir $(DEST)/dpkg_lock &> /dev/null; then
			{ sudo dpkg -i $(SRC_DEB_DEPENDENCIES) $(SRC_DEB) && rm -d $(DEST)/dpkg_lock && break; } || { rm -d $(DEST)/dpkg_lock && exit 1 ; }
		fi
	done

	sudo dkms build mlnx-ofed-kernel/$(OFED_KERNEL_VER_FULL) -k $(KVERSION) -a $(BUILD_ARCH)
	sudo dkms mkbmdeb mlnx-ofed-kernel/$(OFED_KERNEL_VER_FULL) -k $(KVERSION) -a $(BUILD_ARCH)

	# w/a: remove dependencies
	mkdir -p $(DKMS_TMP)/DEBIAN

	dpkg -e $(DKMS_BMDEB)/$(MAIN_TARGET) $(DKMS_TMP)/DEBIAN
	dpkg -x $(DKMS_BMDEB)/$(MAIN_TARGET) $(DKMS_TMP)

	sed -i '/^Depends:/c\Depends:' $(DKMS_TMP)/DEBIAN/control

	dpkg -b $(DKMS_TMP) .

	chown ${USER} $(DERIVED_TARGETS) $(MAIN_TARGET)
	mv $(DERIVED_TARGETS) $* $(DEST)/

	rm -rf $(DKMS_TMP)

	popd
	popd

	sudo mv /bin/uname.orig /bin/uname

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
