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
####  KConfig Processing                                                    ####
################################################################################

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


class KConfigTask():
    def __init__(self, args):
        self.args = args


    def read_data(self):
        KCFGData.x86_base = FileHandler.read_kconfig(self.args.config_base_amd)
        KCFGData.x86_updated = FileHandler.read_kconfig(self.args.config_inc_amd)
        if os.path.isfile(self.args.config_inc_down_amd):
            print(" -> Downstream Config for x86 found..")
            KCFGData.x86_down = FileHandler.read_kconfig(self.args.config_inc_down_amd)

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
