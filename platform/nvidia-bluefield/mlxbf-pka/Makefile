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

MLXBF_PKA = mlxbf-pka-${MLXBF_PKA_DRIVER_VERSION}
MLXBF_PKA_TAR = ${MLXBF_PKA}.tar.gz
MODULE_DIR := $(shell pwd)/${MLXBF_PKA}

$(addprefix $(DEST)/, $(MLXBF_PKA_DRIVER)): $(DEST)/% :
	rm -rf ./mlxbf-pka-$(MLXBF_PKA_DRIVER_VERSION)
	wget -N https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(MLXBF_PKA_TAR)
	tar -z -f $(MLXBF_PKA_TAR) -x

	pushd ${MLXBF_PKA}

	# Build the package
ifeq ($(CROSS_BUILD_ENVIRON), y)
	make -C /lib/modules/$(KVERSION)/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- M=$(MODULE_DIR)
else
	make -C /lib/modules/$(KVERSION)/build M=$(MODULE_DIR)
endif

	mv ${MLXBF_PKA_DRIVER} $(DEST)/
	popd
