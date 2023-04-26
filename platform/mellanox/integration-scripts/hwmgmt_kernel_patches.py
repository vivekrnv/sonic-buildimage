#!/usr/bin/env python

import os
import sys
import shutil
import argparse
import copy
import difflib

from helper import *

class Data:
    # list of new upstream patches
    new_up = list()
    # list of new non-upstream patches
    new_non_up = list()
    # current series file raw data
    old_series = list()
    # current non-upstream patch list
    old_non_up = list()
    # New series file written by hw_mgmt integration script
    new_series = list()
    # List of new opts written by hw_mgmt integration script
    updated_kcfg = list(tuple())
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
    # current kcfg opts
    current_kcfg = list(tuple())
    # current raw kconfig exclude data
    kcfg_exclude = list()

class HwMgmtAction(Action):

    @staticmethod
    def get(args):
        action = None
        if args.action.lower() == "pre":
            action = PreProcess(args)
        elif args.action.lower() == "post":
            action = PostProcess(args)
        
        if not action.check():
            print("-> ERR: Argument Checks Failed")
            sys.exit(1)

        return action

    def check(self):
        if not self.args.config_inclusion:
            print("-> ERR: config_inclusion is missing")
            return False

        if not self.args.build_root:
            print("-> ERR: build_root is missing")
            return False
        
        if not os.path.isfile(self.args.config_inclusion):
            print("-> ERR: config_inclusion {} doesn't exist".format(self.args.config_inclusion))
            return False
        
        if not os.path.exists(self.args.build_root):
            print("-> ERR: Build Root {} doesn't exist".format(self.args.build_root))
            return False

        return True

class PreProcess(HwMgmtAction):
    def __init__(self, args):
        super().__init__(args)

    def check(self):
        return super(PreProcess, self).check()

    def perform(self):
        """ Move MLNX Kconfig to the loc pointed by config_inclusion """
        kcfg_sec = FileHandler.read_kconfig_inclusion(os.path.join(self.args.build_root, SLK_KCONFIG))
        writable_opts = KCFG.get_writable_opts(KCFG.parse_opts_strs(kcfg_sec))
        FileHandler.write_lines(self.args.config_inclusion, writable_opts)
        print("-> OPTS written to temp config_inclusion file: \n{}".format(FileHandler.read_strip(self.args.config_inclusion, True)))
    
class PostProcess(HwMgmtAction):
    def __init__(self, args):
        super().__init__(args)
    
    def check(self):
        if not super(PostProcess, self).check():
            return False

        if not (self.args.patches and os.path.exists(self.args.patches)):
            print("-> ERR: upstream patch directory is missing ")
            return False

        if not (self.args.non_up_patches and os.path.exists(self.args.non_up_patches)):
            print("-> ERR: non upstream patch directory is missing")
            return False

        if not (self.args.series and os.path.isfile(self.args.series)):
            print("-> ERR: series file doesn't exist {}".format(self.args.series))
            return False

        if not (self.args.current_non_up_patches and os.path.exists(self.args.current_non_up_patches)):
            print("-> ERR: current non_up_patches doesn't exist {}".format(self.args.current_non_up_patches))
            return False

        return True

    def read_data(self):
        # Read the data written by hw-mgmt script into the internal Data Structures
        Data.new_series = FileHandler.read_strip_minimal(self.args.series)
        Data.old_series = FileHandler.read_raw(os.path.join(self.args.build_root, SLK_SERIES))
        Data.old_non_up = FileHandler.read_strip_minimal(self.args.current_non_up_patches)

        # Read the new kcfg
        new_cfg = FileHandler.read_kconfig_inclusion(self.args.config_inclusion, None)
        Data.updated_kcfg = KCFG.parse_opts_strs(new_cfg)

        # entire current config, [common] + [amd64]
        all_kcfg = FileHandler.read_kconfig_parser(os.path.join(self.args.build_root, SLK_KCONFIG))
        Data.current_kcfg = []
        for hdr in HDRS:
            Data.current_kcfg.extend(all_kcfg.get(hdr, []))
        Data.current_kcfg = KCFG.parse_opts_strs(Data.current_kcfg)

        Data.kcfg_exclude = FileHandler.read_raw(os.path.join(self.args.build_root, SLK_KCONFIG_EXCLUDE))

        new_up = set(FileHandler.read_dir(self.args.patches, "*.patch"))
        new_non_up = set(FileHandler.read_dir(self.args.non_up_patches, "*.patch"))

        for patch in Data.new_series:
            if patch in new_up:
                Data.new_up.append(patch)
            elif patch in new_non_up:
                Data.new_non_up.append(patch)
            else:
                print("-> FATAL: Patch {} not found either in upstream or non-upstream list".format(patch))
                if not self.args.is_test:
                    sys.exit(1)

    def find_mlnx_hw_mgmt_markers(self):
        """ Find the indexes where the current mlnx patches sits in SLK_SERIES file """
        (Data.i_mlnx_start, Data.i_mlnx_end) = FileHandler.find_marker_indices(Data.old_series, marker=HW_MGMT_MARKER)
        if Data.i_mlnx_start < 0 or Data.i_mlnx_end > len(Data.old_series):
            print("-> FATAL mellanox_hw_mgmt markers not found. Couldn't continue.. exiting")
            sys.exit()

    def rm_old_up_mlnx(self):
        """ Delete the old mlnx upstream patches """
        print("\n -> POST: Removed the following upstream patches:")
        index = Data.i_mlnx_start
        while index <= Data.i_mlnx_end:
            file_n = os.path.join(self.args.build_root, os.path.join(SLK_PATCH_LOC, Data.old_series[index].strip()))
            if os.path.isfile(file_n):
                print(Data.old_series[index].strip())
                os.remove(file_n)
            index = index + 1

    def mv_new_up_mlnx(self):
        for patch in Data.new_up:
            src_path = os.path.join(self.args.patches, patch)
            shutil.copy(src_path, os.path.join(self.args.build_root, SLK_PATCH_LOC))

    def write_final_slk_series(self):
        tmp_new_up = [d+"\n" for d in Data.new_up]
        Data.up_slk_series = Data.old_series[0:Data.i_mlnx_start+1] + tmp_new_up + Data.old_series[Data.i_mlnx_end:]
        print("\n -> POST: Updated sonic-linux-kernel/series file: \n{}".format("".join(Data.up_slk_series)))
        FileHandler.write_lines(os.path.join(self.args.build_root, SLK_SERIES), Data.up_slk_series, True)

    def rm_old_non_up_mlnx(self):
        """ Remove the old non-upstream patches 
        """
        print("\n -> POST: Removed the following supposedly non-upstream patches:")
        # Remove all the old patches and any patches that got accepted with this kernel version
        for patch in Data.old_non_up + Data.new_up:
            file_n = os.path.join(self.args.build_root, os.path.join(NON_UP_PATCH_LOC, patch))
            if os.path.isfile(file_n):
                print(patch)
                os.remove(file_n)

        # Make sure the dir is now empty as all these patches are of hw-mgmt
        files = FileHandler.read_dir(os.path.join(self.args.build_root, NON_UP_PATCH_LOC), "*.patch")
        if files:
            # TODO: When there are SDK non-upstream patches, the logic has to be updated
            print("\n -> FATAL: Patches Remaining in {}: \n{}".format(NON_UP_PATCH_LOC, files))
            sys.exit(1)
        
    def mv_new_non_up_mlnx(self):
        for patch in Data.new_non_up:
            src_path = os.path.join(self.args.non_up_patches, patch)
            shutil.copy(src_path, os.path.join(self.args.build_root, NON_UP_PATCH_LOC))
    
    def construct_series_with_non_up(self):
        Data.agg_slk_series = copy.deepcopy(Data.up_slk_series) 
        lines = ["# Current non-upstream patch list, should be updated by hwmgmt_kernel_patches.py script"]
        for index, patch in enumerate(Data.new_series):
            patch = patch + "\n"
            if patch not in Data.agg_slk_series:
                if index == 0:
                    # if the first patch is a non-upstream patch, then use the marker as the prev index
                    prev_patch = Data.old_series[Data.i_mlnx_start]
                else:    
                    prev_patch = Data.new_series[index-1] + "\n"
                if prev_patch not in Data.agg_slk_series:
                    print("\n -> FATAL: ERR: patch {} is not found in agg_slk_series list: \n {}".format(prev_patch, "".join(Data.agg_slk_series)))
                    sys.exit(1)
                index_prev_patch =  Data.agg_slk_series.index(prev_patch)
                if index_prev_patch < len(Data.agg_slk_series) - 1:
                    Data.agg_slk_series = Data.agg_slk_series[0:index_prev_patch+1] + [patch] +  Data.agg_slk_series[index_prev_patch + 1:]
                else:
                    Data.agg_slk_series = Data.agg_slk_series + [patch]
                print("\n -> INFO: patch {} added to agg_slk_series:".format(patch.strip()))
                lines.append(patch.strip())

        # Update the non_up_current_patch_list file
        FileHandler.write_lines(self.args.current_non_up_patches, lines)
        print("\n -> POST: series file updated with non-upstream patches \n{}".format("".join(Data.agg_slk_series)))

    def write_series_diff(self):
        diff = difflib.unified_diff(Data.up_slk_series, Data.agg_slk_series, fromfile='a/patch/series', tofile="b/patch/series", lineterm="\n")
        lines = []
        for line in diff:
            lines.append(line)
        print("\n -> POST: final series.diff \n{}".format("".join(lines)))
        FileHandler.write_lines(os.path.join(self.args.build_root, NON_UP_PATCH_DIFF), lines, True)
    
    def check_kconfig_conflicts(self):
        # current config under mellanox marker
        old_mlnx_kcfg =  FileHandler.read_kconfig_inclusion(os.path.join(self.args.build_root, SLK_KCONFIG))
        old_mlnx_kcfg = KCFG.parse_opts_strs(old_mlnx_kcfg)

        print("-> INFO: [common] + [amd64] Kconfig: \n{}".format("\n".join(KCFG.get_writable_opts(Data.current_kcfg))))
        print("-> INFO: current mellanox marker Kconfig: \n{}".format("\n".join(KCFG.get_writable_opts(old_mlnx_kcfg))))

        # Filter the mellanox config from current config
        conflict_prone = set(Data.current_kcfg)
        for kcfg in old_mlnx_kcfg:
            if kcfg in conflict_prone:
                conflict_prone.remove(kcfg)

        print("-> INFO: conflict prone Kconfig: \n{}".format("\n".join(KCFG.get_writable_opts(list(conflict_prone)))))
        print("-> INFO: updated kconfig for mellanox marker: \n{}".format("\n".join(KCFG.get_writable_opts(Data.updated_kcfg))))

        # check for conflicts
        has_conflict = False
        for (cfg, val) in Data.updated_kcfg:
            for (cfg_o, val_o) in conflict_prone:
                if cfg == cfg_o and val != val_o:
                    print("-> ERR Conflict seen on the following kconfig: {}, old_opt: {}, new_opt: {}".format(cfg, val_o, val))
                    has_conflict = True
        return has_conflict

    def handle_exclusions(self):
        new_lines = []
        curr_hdr = ""
        for line_raw in Data.kcfg_exclude:
            line = line_raw.strip()
            should_exclude = False
            if line:
                match = re.search(KCFG_HDR_RE, line)
                if match:
                    curr_hdr = match.group(1)
                else:
                    for (kcfg, _) in Data.updated_kcfg:
                        if kcfg == line and curr_hdr in HDRS:
                            should_exclude = True
            if not should_exclude:
                new_lines.append(line_raw)
        FileHandler.write_lines(os.path.join(self.args.build_root, SLK_KCONFIG_EXCLUDE), new_lines, True)
        print("-> INFO: updated kconfig-exclusion: \n{}".format("".join(FileHandler.read_raw(os.path.join(self.args.build_root, SLK_KCONFIG_EXCLUDE)))))

    def perform(self):
        """ Read the data output from the deploy_kernel_patches.py script 
            and move to appropriate locations """
        self.read_data()
        self.find_mlnx_hw_mgmt_markers()
        # Find and report conflicts in new kconfig
        if self.check_kconfig_conflicts():
            print("-> FATAL Conflicts in kconfig-inclusion detected, exiting...")
            sys.exit(1)
        else:
            # Write the new kcfg to the new file
            path = os.path.join(self.args.build_root, SLK_KCONFIG)
            FileHandler.write_lines_marker(path, KCFG.get_writable_opts(Data.updated_kcfg), MLNX_KFG_MARKER)
        self.handle_exclusions()
        # Handle Upstream patches
        self.rm_old_up_mlnx()
        self.mv_new_up_mlnx()
        self.write_final_slk_series()
        # Handle Non Upstream patches
        self.rm_old_non_up_mlnx()
        self.mv_new_non_up_mlnx()
        self.construct_series_with_non_up()
        self.write_series_diff()


def create_parser():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("action", type=str, choices=["pre", "post"])

    # Optional arguments
    parser.add_argument("--patches", type=str)
    parser.add_argument("--non_up_patches", type=str)
    parser.add_argument("--config_inclusion", type=str)
    parser.add_argument("--series", type=str)
    parser.add_argument("--current_non_up_patches", type=str)
    parser.add_argument("--build_root", type=str)
    parser.add_argument("--is_test", action="store_true")
    return parser


if __name__ == '__main__':
    parser = create_parser()
    action = HwMgmtAction.get(parser.parse_args())
    action.perform()
