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

MLXBF2_GPIO = gpio-mlxbf2-${MLXBF2_GPIO_DRIVER_VERSION}
MLXBF2_GPIO_TAR = ${MLXBF2_GPIO}.tar.gz
MODULE_DIR := $(shell pwd)/${MLXBF2_GPIO}

$(addprefix $(DEST)/, $(MLXBF2_GPIO_DRIVER)): $(DEST)/% :
	rm -rf ./gpio-mlxbf2-$(MLXBF2_GPIO_DRIVER_VERSION)
	wget -N "https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(MLXBF2_GPIO_TAR)"
	tar -z -f $(MLXBF2_GPIO_TAR) -x

	pushd ${MLXBF2_GPIO}

	# Build the package
	make -C /lib/modules/$(KVERSION)/build M=$(MODULE_DIR)

	mv ${MLXBF2_GPIO_DRIVER} $(DEST)/
	popd
