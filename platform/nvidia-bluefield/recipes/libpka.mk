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

LIBPKA_DRIVER_VERSION = 1.3
LIBPKA_DEB = libpka1_${LIBPKA_DRIVER_VERSION}-1_arm64.deb

$(LIBPKA_DEB)_SRC_PATH = $(PLATFORM_PATH)/libpka
$(LIBPKA_DEB)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_DEBS += $(LIBPKA_DEB)

export LIBPKA_DRIVER_VERSION
export LIBPKA_DEB
