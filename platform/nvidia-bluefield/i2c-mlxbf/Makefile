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

MLXBF_I2C = i2c-mlxbf-${MLXBF_I2C_DRIVER_VERSION}

$(addprefix $(DEST)/, $(MLXBF_I2C_DRIVER)): $(DEST)/% :
	rm -rf ${MLXBF_I2C}*
	../recipes/get-soc-package.sh ${BSD_BASE_SOURCE_URL} ${MLXBF_I2C}

	pushd ${MLXBF_I2C}

	# Build the package
	DEB_BUILD_OPTIONS=nocheck KVER=$(KVERSION) WITH_DKMS=0 dpkg-buildpackage -rfakeroot -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)

	mv $* $(DEST)/

	popd
