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

MLXBF_GIGE = mlxbf-gige-${MLXBF_GIGE_DRIVER_VERSION}
MLXBF_GIGE_TAR = ${MLXBF_GIGE}.tar.gz
MODULE_DIR := $(shell pwd)/${MLXBF_GIGE}

$(addprefix $(DEST)/, $(MLXBF_GIGE_DRIVER)): $(DEST)/% :
	rm -rf ./mlxbf-gige-$(MLXBF_GIGE_DRIVER_VERSION)
	wget -N "https://linux.mellanox.com/public/repo/bluefield/${BSD_VER}/extras/SOURCES/$(MLXBF_GIGE_TAR)"
	tar -z -f $(MLXBF_GIGE_TAR) -x

	pushd ${MLXBF_GIGE}

	# Build the package
	make -C /lib/modules/$(KVERSION)/build M=$(MODULE_DIR)

	mv ${MLXBF_GIGE_DRIVER} $(DEST)/
	popd
