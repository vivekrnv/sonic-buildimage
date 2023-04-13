#!/usr/bin/env python

import os
import sys
import shutil
import argparse
import copy
import difflib

from helper import *

class Data:
    # old sonic-linux-kernel series file 
    old_series = list()
    # updated sonic-linux-kernel series file
    new_series = list()
    # list of any new SDK patches to add
    new_patches = list()
    # list of current patch list in sonic-linux-kernel
    old_patches = list()
    # index of the mlnx_hw_mgmt patches start marker in old_series
    i_sdk_start = -1 
    # index of the mlnx_hw_mgmt patches end marker in old_series
    i_sdk_end = -1
    # kernel directory to consider the patches
    k_dir = ""

class SDKAction(Action):
    def __init__(self, args):
        super().__init__(args)

    def check(self):
        if not (self.args.patches and os.path.exists(self.args.patches)):
            print("-> ERR: patch directory is missing ")
            return False
    
        if not (self.args.build_root and os.path.exists(self.args.build_root)):
            print("-> ERR: build_root is missing")
            return False

        return True
    
    def read_data(self):
        Data.old_series = FileHandler.read_raw(os.path.join(self.args.build_root, SLK_SERIES))
    
    def find_sdk_patches(self):
        (Data.i_sdk_start, Data.i_sdk_end) = FileHandler.find_marker_indices(Data.old_series, SDK_MARKER)
        if Data.i_sdk_start < 0 or Data.i_sdk_end > len(Data.old_series):
            print("-> FATAL mellanox_sdk marker not found. Couldn't continue.. exiting")
            sys.exit(1)

        print("-> INFO mellanox_sdk markers found. start: {}, end: {}".format(Data.i_sdk_start, Data.i_sdk_end))
        for index in range(Data.i_sdk_start+1, Data.i_sdk_end):
            patch = Data.old_series[index].strip()
            if patch:
                Data.old_patches.append(Data.old_series[index].strip())
        print("-> INFO Current mellanox sdk upstream patches. \n{}".format("\n".join(Data.old_patches)))

    def get_kernel_dir(self):
        # Get the kernel dir name to get the patches
        try:
            (kernel, major, minor) = self.args.sonic_kernel_ver.split(".")
        except Exception as e:
            print("-> FATAL Kernel formatting error: " + str(e))
            sys.exit(1)
        
        Data.k_dir = os.path.join(KERNEL_BACKPORTS, "{}.{}.{}".format(kernel, major, minor))
        if os.path.exists(os.path.join(self.args.patches, Data.k_dir)):
            return 
        
        # if the k_dir with actual minor doesn't exit, use the patches generated against kernel.major
        Data.k_dir = os.path.join(KERNEL_BACKPORTS, "{}.{}.{}".format(kernel, major, "0"))
        path_to_check = os.path.join(self.args.patches, Data.k_dir)
        if os.path.exists(path_to_check):
            return 
        else:
            print("-> FATAL Kernel dir with patches doesn't exist: {}".format(path_to_check))
            sys.exit(1)

    def process_patches(self):
        print(Data.new_patches, Data.old_patches)
        if set(Data.new_patches) == set(Data.old_patches):
            return (False, [], [])
        new_patches = [patch + "\n" for patch in Data.new_patches]
        Data.new_series = Data.old_series[0:Data.i_sdk_start+1] + new_patches + Data.old_series[Data.i_sdk_end:]
        return (True, Data.new_patches, Data.old_patches)
    
    def process_update(self, patches_add, patches_del):
        src_path = os.path.join(self.args.patches, Data.k_dir)
        dst_path = os.path.join(self.args.build_root, SLK_PATCH_LOC)

        for patch in patches_del:
            print("-> Deleting patch: " + patch)
            os.remove(os.path.join(dst_path, patch))

        for patch in patches_add:
            print("-> Adding patch: " + patch)
            shutil.copy(os.path.join(src_path, patch), dst_path)

        FileHandler.write_lines(os.path.join(self.args.build_root, SLK_SERIES), Data.new_series, True)
        print("-> INFO Updated sonic-linux-kernel series file \n{}".format("".join(Data.new_series)))

    def get_new_patches(self):
        patches_path = os.path.join(self.args.patches, Data.k_dir)
        Data.new_patches = FileHandler.read_dir(patches_path, "*.patch")
        Data.new_patches.sort()

    def perform(self):
        self.read_data()
        self.find_sdk_patches()
        self.get_kernel_dir()
        self.get_new_patches()
        (update_required, patches_add, patches_del) = self.process_patches()
        if update_required:
            self.process_update(patches_add, patches_del)

def create_parser():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Optional arguments
    parser.add_argument("--sonic_kernel_ver", type=str)
    parser.add_argument("--patches", type=str)
    parser.add_argument("--build_root", type=str)
    return parser

if __name__ == '__main__':
    parser = create_parser()
    action = SDKAction(parser.parse_args())
    action.check()
    action.perform()