#!/usr/bin/env python
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

import os
import sys
import shutil
import argparse
import copy
import difflib

from helper import *

################################################################################
####  Global Variables and Helper methods                                   ####
################################################################################

COMMIT_TITLE = "Intgerate HW-MGMT {} Changes"

PATCH_TABLE_LOC = "platform/mellanox/hw-management/hw-mgmt/recipes-kernel/linux/"
PATCHWORK_LOC = "linux-{}/patchwork"
PATCH_TABLE_NAME = "Patch_Status_Table.txt"
PATCH_TABLE_DELIMITER = "----------------------"
PATCH_NAME = "patch name"
COMMIT_ID = "Upstream commit id"

# Strips the subversion
def get_kver(k_version):
    major, minor, subversion = k_version.split(".")
    k_ver = "{}.{}".format(major, minor)
    return k_ver

def trim_array_str(str_list):
    ret = [elem.strip() for elem in str_list]
    return ret

def get_line_elements(line):
    columns_raw = line.split("|")
    if len(columns_raw) < 3:
        return False
    # remove empty firsta and last elem
    columns_raw = columns_raw[1:-1]
    columns = trim_array_str(columns_raw)
    return columns

def load_patch_table(path, k_ver):
    patch_table_filename = os.path.join(path, PATCH_TABLE_NAME)
    print("Loading patch table {} kver:{}".format(patch_table_filename, k_ver))

    if not os.path.isfile(patch_table_filename):
        print("-> ERR: file {} not found".format(patch_table_filename))
        return None

    # opening the file
    patch_table_file = open(patch_table_filename, "r")
    # reading the data from the file
    patch_table_data = patch_table_file.read()
    # splitting the file data into lines
    patch_table_lines = patch_table_data.splitlines()
    patch_table_file.close()

    # Extract patch table for specified kernel version
    kversion_line = "Kernel-{}".format(k_ver)
    table_ofset = 0
    for table_ofset, line in enumerate(patch_table_lines):
        if line == kversion_line:
            break

    # if kernel version not found
    if table_ofset >= len(patch_table_lines)-5:
        print ("Err: kernel version {} not found in {}".format(k_ver, patch_table_filename))
        return None

    table = []
    delimiter_count = 0
    column_names = None
    for idx, line in enumerate(patch_table_lines[table_ofset:]):
        if PATCH_TABLE_DELIMITER in line:
            delimiter_count += 1
            if delimiter_count >= 3:
                print ("Err: too much leading delimers line #{}: {}".format(table_ofset + idx, line))
                return None
            elif table:
                break
            continue

        # line without delimiter but header still not found
        if delimiter_count > 0:
            if not column_names:
                column_names = get_line_elements(line)
                if not column_names:
                    print ("Err: parsing table header line #{}: {}".format(table_ofset + idx, line))
                    return None
                delimiter_count = 0
                continue
            elif column_names:
                line_arr = get_line_elements(line)
                if len(line_arr) != len(column_names):
                    print ("Err: patch table wrong format linex #{}: {}".format(table_ofset + idx, line))
                    return None
                else:
                    table_line = dict(zip(column_names, line_arr))
                    table.append(table_line)
    return table

################################################################################
####  Shared Data                                                           ####
################################################################################


class Data:
    # list of new upstream patches
    new_up = list()
    # list of new non-upstream patches
    new_non_up = list()
    # old upstream patches
    old_up_patches = list()
    # current series file raw data
    old_series = list()
    # current non-upstream patch list
    old_non_up = list()
    # New series file written by hw_mgmt integration script
    new_series = list()
    # index of the mlnx_hw_mgmt patches start marker in old_series
    i_mlnx_start = -1 
    # index of the mlnx_hw_mgmt patches end marker in old_series
    i_mlnx_end = -1
    # Updated sonic-linux-kernel/patch/series file contents
    up_slk_series = list()
    # SLK series file content updated with non-upstream patches, used to generate diff
    agg_slk_series = list()
    # Diff to be written into the series.patch file
    agg_slk_series_diff = list()
    # kernel version
    k_ver = ""


class KCFGData:
    x86_base = OrderedDict()
    x86_updated = OrderedDict()
    arm_base = OrderedDict()
    arm_updated = OrderedDict()
    x86_incl = OrderedDict()
    arm_incl = OrderedDict()
    x86_excl = OrderedDict()
    arm_excl = OrderedDict()
    x86_down = OrderedDict()
    arm_down = OrderedDict()
    noarch_incl = OrderedDict()
    noarch_excl = OrderedDict()
    noarch_down = OrderedDict()


################################################################################
####  KConfig Processing                                                    ####
################################################################################


class KConfigTask():
    def __init__(self, args):
        self.args = args


    def read_data(self):
        KCFGData.x86_base = FileHandler.read_kconfig(self.args.config_base)
        KCFGData.x86_updated = FileHandler.read_kconfig(self.args.config_inc)
        if os.path.isfile(self.args.config_inc_down):
            print(" -> Downstream Config for x86 found..")
            KCFGData.x86_down = FileHandler.read_kconfig(self.args.config_inc_down)

        KCFGData.arm_base = FileHandler.read_kconfig(self.args.config_base_arm)
        KCFGData.arm_updated = FileHandler.read_kconfig(self.args.config_inc_arm)
        if os.path.isfile(self.args.config_inc_down_arm):
            print(" -> Downstream Config for arm64 found..")
            KCFGData.arm_down = FileHandler.read_kconfig(self.args.config_inc_down_arm)
        return 


    def parse_inc_exc(self, base: OrderedDict, updated: OrderedDict):
        # parse the updates/deletions in the Kconfig
        add, remove = OrderedDict(), copy.deepcopy(base)
        for (key, val) in updated.items():
            if val != base.get(key, "empty"):
                add[key] = val
            # items remaining in remove are the ones to be excluded
            if key in remove:
                del remove[key]
        return add, remove


    def parse_noarch_inc_exc(self):
        # Filter the common inc/excl out from the arch specific inc/excl
        x86_incl_base = copy.deepcopy(KCFGData.x86_incl)
        for (key, val) in x86_incl_base.items():
            if key in KCFGData.arm_incl and val == KCFGData.arm_incl[key]:
                print("-> INFO: NoArch KConfig Inclusion {}:{} found and moving to common marker".format(key, val))
                del KCFGData.arm_incl[key]
                del KCFGData.x86_incl[key]
                KCFGData.noarch_incl[key] = val

        x86_excl_base = copy.deepcopy(KCFGData.x86_excl)
        for (key, val) in x86_excl_base.items():
            if key in KCFGData.arm_excl:
                print("-> INFO: NoArch KConfig Exclusion {} found and moving to common marker".format(key))
                del KCFGData.arm_excl[key]
                del KCFGData.x86_excl[key]
                KCFGData.noarch_excl[key] = val

        if not (KCFGData.x86_down or KCFGData.arm_down):
            return

        # Filter the common inc config from the downstream kconfig
        x86_down_base = copy.deepcopy(KCFGData.x86_down)
        for (key, val) in x86_down_base.items():
            if key in KCFGData.arm_down:
                print("-> INFO: NoArch KConfig Downstream Inclusion {} found and moving to common marker".format(key))
                del KCFGData.arm_down[key]
                del KCFGData.x86_down[key]
                KCFGData.noarch_down[key] = val


    def get_kconfig_inc(self) -> list:
        kcfg_inc_raw = FileHandler.read_raw(os.path.join(self.args.build_root, SLK_KCONFIG))
        # Insert common config
        noarch_start, noarch_end = FileHandler.find_marker_indices(kcfg_inc_raw, MLNX_NOARCH_MARKER)
        kcfg_inc_raw = FileHandler.insert_kcfg_data(kcfg_inc_raw, noarch_start, noarch_end, KCFGData.noarch_incl)
        # Insert x86 config
        x86_start, x86_end = FileHandler.find_marker_indices(kcfg_inc_raw, MLNX_KFG_MARKER)
        kcfg_inc_raw = FileHandler.insert_kcfg_data(kcfg_inc_raw, x86_start, x86_end, KCFGData.x86_incl)
        # Insert arm config
        arm_start, arm_end = FileHandler.find_marker_indices(kcfg_inc_raw, MLNX_ARM_KFG_MARKER)
        kcfg_inc_raw = FileHandler.insert_kcfg_data(kcfg_inc_raw, arm_start, arm_end, KCFGData.arm_incl)
        print("\n -> INFO: kconfig-inclusion file is generated \n {}".format("".join(kcfg_inc_raw)))
        return kcfg_inc_raw


    def get_downstream_kconfig_inc(self, new_kcfg_upstream) -> list:
        kcfg_final = copy.deepcopy(new_kcfg_upstream)
        # insert common Kconfig
        noarch_start, noarch_end = FileHandler.find_marker_indices(kcfg_final, MLNX_NOARCH_MARKER)        
        noarch_final = OrderedDict(list(KCFGData.noarch_incl.items()) + list(KCFGData.noarch_down.items()))
        kcfg_final = FileHandler.insert_kcfg_data(kcfg_final, noarch_start, noarch_end, noarch_final)
        # insert x86 Kconfig
        x86_start, x86_end = FileHandler.find_marker_indices(kcfg_final, MLNX_KFG_MARKER)        
        x86_final = OrderedDict(list(KCFGData.x86_incl.items()) + list(KCFGData.x86_down.items()))
        kcfg_final = FileHandler.insert_kcfg_data(kcfg_final, x86_start, x86_end, x86_final)
        # insert arm Kconfig
        arm_start, arm_end = FileHandler.find_marker_indices(kcfg_final, MLNX_ARM_KFG_MARKER)        
        arm_final = OrderedDict(list(KCFGData.arm_incl.items()) + list(KCFGData.arm_down.items()))
        kcfg_final = FileHandler.insert_kcfg_data(kcfg_final, arm_start, arm_end, arm_final)
        # assert arm_final != KCFGData.arm_incl
        # generate diff
        diff = difflib.unified_diff(new_kcfg_upstream, kcfg_final, fromfile='a/patch/kconfig-inclusions', tofile="b/patch/kconfig-inclusions", lineterm="\n")
        lines = []
        for line in diff:
            lines.append(line)
        print("\n -> INFO: kconfig-inclusion.patch file is generated \n{}".format("".join(lines)))
        return lines


    def get_kconfig_excl(self) -> list:
        # noarch_excl
        kcfg_excl_raw = FileHandler.read_raw(os.path.join(self.args.build_root, SLK_KCONFIG_EXCLUDE))
        # insert common Kconfig
        noarch_start, noarch_end = FileHandler.find_marker_indices(kcfg_excl_raw, MLNX_NOARCH_MARKER)
        kcfg_excl_raw = FileHandler.insert_kcfg_excl_data(kcfg_excl_raw, noarch_start, noarch_end, KCFGData.noarch_excl)
        # insert x86 Kconfig
        x86_start, x86_end = FileHandler.find_marker_indices(kcfg_excl_raw, MLNX_KFG_MARKER)
        kcfg_excl_raw = FileHandler.insert_kcfg_excl_data(kcfg_excl_raw, x86_start, x86_end, KCFGData.x86_excl)
        # insert arm Kconfig
        arm_start, arm_end = FileHandler.find_marker_indices(kcfg_excl_raw, MLNX_ARM_KFG_MARKER)
        kcfg_excl_raw = FileHandler.insert_kcfg_excl_data(kcfg_excl_raw, arm_start, arm_end, KCFGData.arm_excl)
        print("\n -> INFO: kconfig-exclusion file is generated \n{}".format("".join(kcfg_excl_raw)))
        return kcfg_excl_raw


    def perform(self):
        self.read_data()
        KCFGData.x86_incl, KCFGData.x86_excl = self.parse_inc_exc(KCFGData.x86_base, KCFGData.x86_updated)
        KCFGData.arm_incl, KCFGData.arm_excl = self.parse_inc_exc(KCFGData.arm_base, KCFGData.arm_updated)
        self.parse_noarch_inc_exc()
        # Get the updated kconfig-inclusions
        kcfg_inc_upstream = self.get_kconfig_inc()
        FileHandler.write_lines(os.path.join(self.args.build_root, SLK_KCONFIG), kcfg_inc_upstream, True)
        # Get the kconfig-inclusions.patch
        kcfg_inc_diff = self.get_downstream_kconfig_inc(kcfg_inc_upstream)
        if kcfg_inc_diff:
            FileHandler.write_lines(os.path.join(self.args.build_root, NON_UP_KCFG_INC_DIFF), kcfg_inc_diff, True)
        # Get the updated kconfig-exclusions
        kcfg_excl_upstream = self.get_kconfig_excl()
        FileHandler.write_lines(os.path.join(self.args.build_root, SLK_KCONFIG_EXCLUDE), kcfg_excl_upstream, True)
        return
