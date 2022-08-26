"""
build_dkms script
    Validate the patches 
    Parse override-modules and build a dkms folder with the required source and conf file
"""
import os
import shutil
import subprocess
import sys
import json
import shutil
import argparse

LINUX=""
HWMGMT_VERSION=""
CONFIGURED_ARCH=""
KVERSION=""

EXCLUDE_PATCHES = "exclude-patches"
UPSTREAM_PATCHES = "upstream-patches"
MODULES_JSON = "override-modules.json"
MOD_PATCHES = "sonic-patches/"
PATCHPATH = "../hw-mgmt/recipes-kernel/linux/linux-5.10/"
SONIC_PATCHPATH = "../../../../src/sonic-linux-kernel/patch"

# Makefile used in the root of the dkms directory
# Update it with the subdirs to build
MK = """\
# Makefile for the hw-mgmt modules in the dkms tree.
obj-y += {}
"""
NAME = 'PACKAGE_NAME="hwmgmt"'
VER = 'PACKAGE_VERSION="{}"'
CLEAN_CMD = 'CLEAN[0]="make -C /usr/src/linux-headers-{} M="/var/lib/dkms/hwmgmt/{}/build" clean"'
MK_CMD = 'MAKE[0]="make {} -C /usr/src/linux-headers-{} M="/var/lib/dkms/hwmgmt/{}/build" KERNELDIR=/lib/modules/{}/build modules"'
MOD_NAME = 'BUILT_MODULE_NAME[{}]="{}"'
MOD_LOC = 'BUILT_MODULE_LOCATION[{}]="{}"'
MOD_DEST = 'DEST_MODULE_LOCATION[{}]="{}"'
AUTO_INS = 'AUTOINSTALL="yes"'


# SCHEMA for override-modules.json
# 1) PATH should start with "drivers/".
# 2) Use BLD_LOC field if the module.ko file sits in the subdirs of "path". 
#    If not specified, the *.ko file is searched under PATH
# 3) BLD_OPTS should be of format "opt":"val" Eg: "CONFIG_MLXSW_CORE": "m"
#    This is passed down directly to the make command used by the dkms
PATH = "path" # Mandatory, 
BLD_OPTS = "build_opts" # Optional
BLD_LOC = "build_location" # Optional

""" Helper Methods """ 

def handle_args():
    """ parse arguments and update variables """ 
    parser = argparse.ArgumentParser(description='build_dkms helper script')
    parser.add_argument('linux', type=str, help='Linux Source Version')
    parser.add_argument('hw_mgmt', type=str, help='HW Management Version')
    parser.add_argument('arch', type=str, help='Platform Architecture (Eg: arm64 or amd64)')
    parser.add_argument('kernel_ver', type=str, help='Sonic Kernel Version')
    return parser.parse_args()

def read_json(path) -> dict:
    modules = {}
    with open(path) as om:
        modules = json.load(om)
    return modules

def read_lines(path) -> list:
    data = []
    with open(path) as im:
        data = im.readlines()
    return [l.strip() for l in data]

def write_lines(path, lines: list):
    with open(path, "w") as conf:
        conf.writelines(lines)

def write_data(path, data: str):
    with open(path, "w") as mk:
        mk.write(data)

def read_patches(path: str) -> list:
    patch_list = [f for f in os.listdir(path) if f.endswith(".patch")]
    patch_list = [os.path.join(path, f) for f in patch_list]
    return patch_list

def read_sonic_patches(path: str) -> list:
    return  [f[0:8] for f in os.listdir(path) if f.endswith(".patch")]

def newln(line: str) -> str:
    return line + '\n'

""" Helper Classes """ 

class Data:
    patches = []
    ignore = []
    sonicpatch = []
    upstream = []
    modifiedpatch= []
    modules = {}
    # information regarding the list of the files updated by the patches
    fl = {}

    @staticmethod
    def read_all():
        Data.patches = read_patches(PATCHPATH)
        Data.ignore = read_lines(EXCLUDE_PATCHES)
        Data.sonicpatch = read_sonic_patches(SONIC_PATCHPATH)
        Data.modules = read_json(MODULES_JSON)
        Data.upstream = read_lines(UPSTREAM_PATCHES)
        Data.remove_ignore()
        Data.modifiedpatch = read_patches(MOD_PATCHES)
        Data.fl = Data.extract_modified_files()
        print(json.dumps(Data.fl, indent=4))

    @staticmethod 
    def remove_ignore():
        """ Remove ignore patches from patch list """ 
        for i in Data.ignore:
            try:
                Data.patches.remove([p for p in Data.patches if i.strip() == os.path.basename(p)][0])
            except ValueError:
                print("WARNING Ignored patch {} not included in hw-mgmt patch set.".format(i))
    
    @staticmethod 
    def remove_upstream():
        """ Remove upstreamed patches from patch list """ 
        for i in Data.upstream:
            try:
                Data.patches.remove([p for p in Data.patches if i.strip() == os.path.basename(p)][0])
            except ValueError:
                print("WARNING Upstream patch {} not included in hw-mgmt patch set.".format(i))

    @staticmethod
    def extract_modified_files():
        return {p:[o.split(' ')[1].replace('b/', '')
                for o in subprocess.check_output("grep -h '+++ .*\.[c|h]' {} || true".format(p), shell=True).decode("UTF-8").split('\n')
                if "+++" in o] 
                for p in Data.patches}
        

class Validator:

    @staticmethod
    def check():
        """
        Verify all patches are loaded in
        Make sure if we are loading a patch through DKMS that all modules for that patch successfully resolved
        Make sure if we are not loading a patch through DKMS that it is present in sonic-linux-kernel
        """
        error, msg = False, ""
        for p, files in Data.fl.items():
            if os.path.basename(p)[0:8] not in Data.sonicpatch and os.path.basename(p) not in Data.ignore and os.path.basename(p) not in Data.upstream:
                for f in files:
                    overridden = False
                    for k,v in Data.modules.items():
                        if os.path.commonprefix([f,v[PATH]]) == v[PATH]:
                            overridden = True
                    if not overridden:
                        error = True
                        msg += "Patch {} not in modules or upstream kernel!\n".format(p)
                        break
        if error:
            raise ValueError(msg)


class DKMS():
    """ Build dkms bundle """
    
    def __init__(self):
        self.hwmgmt_dkms_src = "/usr/src/hwmgmt-{}/".format(HWMGMT_VERSION)
        self.paths = []
        self.lines = []
        self.cfg_opts = "" # Capture any config options
        self.module_info = [] # ("mod_name", "id", "build_loc", "dest")

    def add(self, line: str):
        self.lines.append(newln(line))
    
    def add_lns(self, lines: list):
        for line in lines:
            self.add(line)
    
    def rename(self, path):
        """
        drivers/i2c/muxes => i2c_muxes
        """
        components = os.path.normpath(path).split(os.sep)
        if len(components) == 0 or components[0] != 'drivers':
            raise Exception("target source should be under drivers/")
        return "_".join([comp for comp in components[1:]])

    # Build overriden modules (explore combining all of these into single package)
    def create_dkms_src(self):
        os.mkdir(self.hwmgmt_dkms_src)

    def add_hdr(self):
        lns = [NAME, VER.format(HWMGMT_VERSION)]
        self.add_lns(lns)
    
    def add_cln(self):
        self.add(CLEAN_CMD.format(KVERSION, HWMGMT_VERSION))
    
    def parse_module_json(self):
        """
        Construct the following:
           - paths (to copy relevant source dirs)
           - cfg_opts (used in make cmd)
           - module_info (used to construct the modules info in the dkms.conf)
        """
        count = 0
        for mod, keys in Data.modules.items():
            path = keys[PATH]
            loc = self.rename(path)
            dest = os.path.join("/kernel/", path)

            if BLD_LOC in keys:
                loc = os.path.join(loc, keys.get(BLD_LOC))
                dest = os.path.join(dest, keys.get(BLD_LOC))


            for opt, val in keys.get(BLD_OPTS, {}).items():
                self.cfg_opts += "{}={} ".format(opt,val)

            if path not in self.paths:
                self.paths.append(path)
            
            self.module_info.append({"name": mod,
                                    "id": count,
                                    "loc": loc,
                                    "dest": dest})
            count += 1

    def add_mk_cmd(self):
        self.add(MK_CMD.format(self.cfg_opts, KVERSION, HWMGMT_VERSION, KVERSION))

    def add_mod_info(self):
        for info in self.module_info:
            nme = MOD_NAME.format(info["id"], info["name"])
            loc = MOD_LOC.format(info["id"], info["loc"])
            dest = MOD_DEST.format(info["id"], info["dest"])
            self.add_lns([nme, loc, dest])

    def write_mk(self):
        final_mk = MK.format(" ".join(self.rename(path)+"/" for path in self.paths))
        write_data(os.path.join(self.hwmgmt_dkms_src, "Makefile"), final_mk)
        
    def write_dkms_conf(self):
        write_lines(os.path.join(self.hwmgmt_dkms_src, "dkms.conf"), self.lines)
        print(self.lines)

    def move_src_dirs(self):
        for path in self.paths:
            # Move to the dkms folder
            shutil.move(os.path.join("linux-{}".format(LINUX),path), self.hwmgmt_dkms_src)
            leaf = os.path.basename(path)
            mod_nme = self.rename(path)
            # Rename
            os.rename(os.path.join(self.hwmgmt_dkms_src,leaf), os.path.join(self.hwmgmt_dkms_src,mod_nme))

    def build(self):
        self.create_dkms_src()
        self.add_hdr()
        self.add_cln()
        self.parse_module_json()
        self.add_mk_cmd()
        self.add_mod_info()
        self.write_mk()
        self.write_dkms_conf()
        self.move_src_dirs()


if __name__ == "__main__":
    args = handle_args()
    LINUX = args.linux
    HWMGMT_VERSION = args.hw_mgmt
    CONFIGURED_ARCH = args.arch
    KVERSION = args.kernel_ver
    Data.read_all()
    # Validator.check()
    dkms_handle = DKMS()
    dkms_handle.build()

# # Download and unpack kernel (check if this kernel is present in sonic-linux-kernel)
# linux_tar = "linux-{}.tar.gz".format(LINUX)
# sonic_linux_kernel = os.path.join("../../../../src/sonic-linux-kernel", linux_tar)
# if os.path.exists(sonic_linux_kernel):
#     shutil.copy(sonic_linux_kernel, linux_tar)
# else:
#     subprocess.call("wget -nc https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-{}.tar.gz".format(LINUX), shell=True)

# lines = []
# paths = []
# module_lines = []
# cfg_opts = ""

# count = 0
# for mod, keys in modules.items():
#     path = keys[PATH]
#     built_module_location = os.path.basename(path) + keys.get(BLD_LOC, "")
#     for opt, val in keys.get(BLD_OPTS, {}).items():
#         cfg_opts += "{}={} ".format(opt,val)

#     if path not in paths:
#         shutil.move(os.path.join("linux-{}".format(LINUX),path), "/usr/src/hwmgmt-{}/".format(HWMGMT_VERSION)) # Move to correct folder
#         paths.append(path)

#     module_lines += ['BUILT_MODULE_NAME[{}]="{}"\n'.format(count,mod)]
#     module_lines += ['BUILT_MODULE_LOCATION[{}]="{}"\n'.format(count,built_module_location)]
#     module_lines += ['DEST_MODULE_LOCATION[{}]="{}"\n'.format(count, os.path.join("/kernel/", path))]
#     count += 1

# lines += ['MAKE[0]="make {} -C /usr/src/linux-headers-{} M="/var/lib/dkms/hwmgmt/{}/build" KERNELDIR=/lib/modules/{}/build modules"\n'.format(cfg_opts, KVERSION, HWMGMT_VERSION, KVERSION)]
# lines = lines + module_lines
# lines += ['AUTOINSTALL="yes"\n']



