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

MLX_TRIO = mlx-trio-${MLX_TRIO_DRIVER_VERSION}
MLX_TRIO_TAR = ${MLX_TRIO}.tar.gz
MODULE_DIR := $(shell pwd)/${MLX_TRIO}

$(addprefix $(DEST)/, $(MLX_TRIO_DRIVER)): $(DEST)/% :
	rm -rf ${MLX_TRIO} ${MLX_TRIO_TAR}
	wget -N "https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(MLX_TRIO_TAR)"
	tar -z -f $(MLX_TRIO_TAR) -x

	pushd ${MLX_TRIO}

	# Build the package
ifeq ($(CROSS_BUILD_ENVIRON), y)
	make -C /lib/modules/$(KVERSION)/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- M=$(MODULE_DIR)
else
	make -C /lib/modules/$(KVERSION)/build M=$(MODULE_DIR)
endif

	mv ${MLX_TRIO_DRIVER} $(DEST)/
	popd
