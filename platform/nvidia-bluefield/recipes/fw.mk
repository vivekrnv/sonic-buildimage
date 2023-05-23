#
# Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES.
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

FW_BASE_PATH = $(PLATFORM_PATH)/sdk-src/sonic-bluefield-packages/fw
BF3_FW_BASE_URL =

BF3_FW_VERSION = 32.37.1300

BF3_FW_FILE = fw-BlueField-3-rel-$(subst .,_,$(BF3_FW_VERSION)).mfa
$(BF3_FW_FILE)_PATH = $(FW_BASE_PATH)/
$(BF3_FW_FILE)_URL = $(BF3_FW_BASE_URL)/$(BF3_FW_FILE)

BF_FW_FILES = $(BF3_FW_FILE)

export BF3_FW_FILE
export BF_FW_FILES

ifeq ($(BF3_FW_BASE_URL),)
SONIC_COPY_FILES += $(BF_FW_FILES)
else
SONIC_ONLINE_FILES += $(BF_FW_FILES)
endif

