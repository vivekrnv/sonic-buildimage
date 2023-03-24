#
# Copyright (c) 2016-2022 NVIDIA CORPORATION & AFFILIATES.
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
# Mellanox HW Management

MLNX_HW_MANAGEMENT_VERSION = 7.0020.4104

export MLNX_HW_MANAGEMENT_VERSION

MLNX_HW_MANAGEMENT = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_$(CONFIGURED_ARCH).deb
$(MLNX_HW_MANAGEMENT)_SRC_PATH = $(PLATFORM_PATH)/hw-management
$(MLNX_HW_MANAGEMENT)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_MAKE_DEBS += $(MLNX_HW_MANAGEMENT)

TEMP_HW_MGMT_DIR = /tmp/hw_mgmt
PTCH_DIR = $(TEMP_HW_MGMT_DIR)/patch_dir/
NON_UP_PTCH_DIR = $(TEMP_HW_MGMT_DIR)/non_up_patch_dir/
PTCH_LIST  = $(TEMP_HW_MGMT_DIR)/series
KCFG_LIST = $(TEMP_HW_MGMT_DIR)/kconfig
HWMGMT_NONUP_LIST = $(BUILD_WORKDIR)/$($(MLNX_HW_MANAGEMENT)_SRC_PATH)/hwmgmt_nonup_patches
USER_OUTFILE = $(BUILD_WORKDIR)/integrate-mlnx-hw-mgmt_user.out
TMPFILE = /tmp/intg-hw-mgmt.out

integrate-mlnx-hw-mgmt:
	$(FLUSH_LOG)
	rm -rf $(TEMP_HW_MGMT_DIR) $(TMPFILE)
	mkdir -p $(PTCH_DIR) $(NON_UP_PTCH_DIR)
	touch $(PTCH_LIST) $(KCFG_LIST)

	# clean up existing untracked files
	pushd $(BUILD_WORKDIR); git stash; git clean -f -- platform/mellanox/; popd
	pushd $(BUILD_WORKDIR)/src/sonic-linux-kernel; git stash; git clean -f -- patch/; popd

	echo "#### Integrate HW-MGMT ${MLNX_HW_MANAGEMENT_VERSION} Kernel Patches into SONiC" > ${USER_OUTFILE}
	pushd $(BUILD_WORKDIR)/$(PLATFORM_PATH) $(LOG_SIMPLE)

	# Run tests
	pushd integration-scripts/tests; pytest-3 -v; popd

	# Pre-processing before runing hw_mgmt script
	integration-scripts/hwmgmt_kernel_patches.py pre \
							--config_inclusion $(KCFG_LIST) \
							--build_root $(BUILD_WORKDIR) $(LOG_SIMPLE)

	$(BUILD_WORKDIR)/$($(MLNX_HW_MANAGEMENT)_SRC_PATH)/hw-mgmt/recipes-kernel/linux/deploy_kernel_patches.py \
							--dst_accepted_folder $(PTCH_DIR) \
							--dst_candidate_folder $(NON_UP_PTCH_DIR) \
							--series_file $(PTCH_LIST) \
							--config_file $(KCFG_LIST) \
							--kernel_version $(KERNEL_VERSION) \
							--os_type sonic $(LOG_SIMPLE)

	# Post-processing
	integration-scripts/hwmgmt_kernel_patches.py post \
							--patches $(PTCH_DIR) \
							--non_up_patches $(NON_UP_PTCH_DIR) \
							--config_inclusion $(KCFG_LIST) \
							--series $(PTCH_LIST) \
							--current_non_up_patches $(HWMGMT_NONUP_LIST) \
							--build_root $(BUILD_WORKDIR) $(LOG_SIMPLE)
	
	# Commit the changes in linux kernel and and log the diff
	pushd $(BUILD_WORKDIR)/src/sonic-linux-kernel
	git add -- patch/; git commit -m "Intgerate HW-MGMT ${MLNX_HW_MANAGEMENT_VERSION} Changes";

	echo -en "\n###-> series file changes in sonic-linux-kernel <-###\n" >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD -- patch/series >> ${USER_OUTFILE}

	echo -en "\n###-> kconfig-inclusions file changes in sonic-linux-kernel <-###\n" >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD -- patch/kconfig-inclusions >> ${USER_OUTFILE}

	echo -en "\n###-> kconfig-exclusions file changes in sonic-linux-kernel <-###\n" >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD -- patch/kconfig-exclusions >> ${USER_OUTFILE}

	echo -en '\n###-> Summary of files updated in sonic-linux-kernel <-###\n' >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD --stat --output=${TMPFILE}
	cat ${TMPFILE} | tee -a ${USER_OUTFILE}
	popd

	# Commit the changes in buildimage and log the diff
	pushd $(BUILD_WORKDIR)
	git add -- $(PLATFORM_PATH); git commit -m "Intgerate HW-MGMT ${MLNX_HW_MANAGEMENT_VERSION} Changes";

	echo -en '\n###-> Non Upstream series.patch changes <-###\n' >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD -- $(PLATFORM_PATH)/non-upstream-patches/series.patch >> ${USER_OUTFILE}

	echo -en '\n###-> Non Upstream patch list file <-###\n' >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD -- $($(MLNX_HW_MANAGEMENT)_SRC_PATH)/hwmgmt_nonup_patches >> ${USER_OUTFILE}
	
	echo -en '\n###-> Summary of buildimage changes <-###\n' >> ${USER_OUTFILE}
	git diff --no-color  HEAD~1 HEAD --stat --output=${TMPFILE} -- $(PLATFORM_PATH)
	cat ${TMPFILE} | tee -a ${USER_OUTFILE}
	popd

	popd $(LOG_SIMPLE)

SONIC_PHONY_TARGETS += integrate-mlnx-hw-mgmt
