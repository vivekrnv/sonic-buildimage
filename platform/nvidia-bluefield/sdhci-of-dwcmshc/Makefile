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

.ONESHELL:
SHELL = /bin/bash

SDHCI_OF_DWCMSHC = sdhci-of-dwcmshc-${SDHCI_OF_DWCMSHC_DRIVER_VERSION}
SDHCI_OF_DWCMSHC_TAR = ${SDHCI_OF_DWCMSHC}.tar.gz

MAIN_TARGET = $(SDHCI_OF_DWCMSHC_DRIVER)
DERIVED_TARGETS =

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Make sure errors will be reported
	set -e

	rm -rf ${SDHCI_OF_DWCMSHC} ${SDHCI_OF_DWCMSHC_TAR}
	wget -N "${BSD_BASE_SOURCE_URL}/${SDHCI_OF_DWCMSHC_TAR}"
	tar -z -f ${SDHCI_OF_DWCMSHC_TAR} -x
	pushd ${SDHCI_OF_DWCMSHC}
	find . -type f -exec touch {} +

	# Build the Debs
	KVER=$(KVERSION) WITH_DKMS=0 dpkg-buildpackage -rfakeroot -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)

	mv $(DERIVED_TARGETS) $* $(DEST)/
	popd

$(addprefix $(DEST)/, $(DERIVED_TARGETS)): $(DEST)/% : $(DEST)/$(MAIN_TARGET)
