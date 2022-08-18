import os
import shutil
import subprocess
import sys
import json
import shutil

LINUX=sys.argv[1]
HWMGMT_VERSION=sys.argv[2]
CONFIGURED_ARCH=sys.argv[3]
KVERSION=sys.argv[4]

# Common Makefile template
MK = """\
#
# Common Makefile for the hw-mgmt sources.
#
obj-y += {}
"""


# JSON Keys
PATH = "path"
BLD_OPTS = "build_opts"

# Get list of patches from hw-mgmt
patchpath = "../hw-mgmt/recipes-kernel/linux/linux-5.10/"
patches = [f for f in os.listdir(patchpath) if f.endswith(".patch")]
patches = [os.path.join(patchpath, f) for f in patches]
patches.sort()

# Get ignored patches and remove from patch set
ignore = []
with open("exclude-patches") as im:
    ignore = im.readlines()
for i in ignore:
    try:
        patches.remove([p for p in patches if i.strip() == os.path.basename(p)][0])
    except ValueError:
        print("WARNING Ignored patch {} not included in hw-mgmt patch set.".format(i))

# with open(os.path.join(patchpath, "series"), "w") as s:
#     s.writelines(["{}\n".format(os.path.basename(p)) for p in patches])

# Get list of patches from SONiC
sonicpath = "../../../../src/sonic-linux-kernel/patch"
sonicpatch = [f[0:8] for f in os.listdir(sonicpath) if f.endswith(".patch")]

# Parse modules from override-modules.yaml file
modules = {}
with open("override-modules.json") as om:
    modules = json.load(om)

# # Download and unpack kernel (check if this kernel is present in sonic-linux-kernel)
# linux_tar = "linux-{}.tar.gz".format(LINUX)
# sonic_linux_kernel = os.path.join("../../../../src/sonic-linux-kernel", linux_tar)
# if os.path.exists(sonic_linux_kernel):
#     shutil.copy(sonic_linux_kernel, linux_tar)
# else:
#     subprocess.call("wget -nc https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-{}.tar.gz".format(LINUX), shell=True)

# subprocess.call("rm -rf linux-{}".format(LINUX), shell=True)
# subprocess.call("tar xf {}".format(linux_tar), shell=True)
# subprocess.call("git init; git add -A; git commit -m 'Init'; stg init; stg import -s {}".format(os.path.join("..", patchpath, "series")), 
#         shell=True, cwd="linux-{}".format(LINUX))

# Get a list of modified files from hw-mgmt patches
fl = {p:[o.split(' ')[1].replace('b/', '')
            for o in subprocess.check_output("grep -h '+++ .*\.[c|h]' {} || true".format(p), shell=True).decode("UTF-8").split('\n')
            if "+++" in o] 
            for p in patches}

# Get upstream patches (these are patches merged into the kernel between the hw-mgmt version and the sonic version) 
upstream = []
with open("upstream-patches") as inc:
    upstream = [l.strip() for l in inc.readlines()]

# Verify all patches are loaded in
# Make sure if we are loading a patch through DKMS that all modules for that patch successfully resolved
# Make sure if we are not loading a patch through DKMS that it is present in sonic-linux-kernel
error = False
msg = ""
for p, files in fl.items():
    if os.path.basename(p)[0:8] not in sonicpatch and os.path.basename(p) not in ignore and os.path.basename(p) not in upstream:
        for f in files:
            overridden = any([os.path.commonprefix([f,v]) == v[PATH] for k, v in modules.items()])
            if not overridden:
                error = True
                msg += "Patch {} not in modules or upstream kernel!\n".format(p)
                break
if error: raise ValueError(msg)

# Build overriden modules (explore combining all of these into single package)
os.mkdir("/usr/src/hwmgmt-{}".format(HWMGMT_VERSION))

lines = []
paths = []
module_lines = []
cfg_opts = ""
lines += ['PACKAGE_NAME="hwmgmt"\n']
lines += ['PACKAGE_VERSION="{}"\n'.format(HWMGMT_VERSION)]
lines += ['CLEAN[0]="make -C /usr/src/linux-headers-{} M="/var/lib/dkms/hwmgmt/{}/build" clean"\n'.format(KVERSION, HWMGMT_VERSION)]

count = 0
for mod, keys in modules.items():
    path = keys["path"]
    for opt, val in keys.get(BLD_OPTS, {}).items():
        cfg_opts += "{}={} ".format(opt,val)

    if path not in paths:
        shutil.move(os.path.join("linux-{}".format(LINUX),path), "/usr/src/hwmgmt-{}/".format(HWMGMT_VERSION)) # Move to correct folder
        paths.append(path)
    module_lines += ['BUILT_MODULE_NAME[{}]="{}"\n'.format(count,mod)]
    module_lines += ['BUILT_MODULE_LOCATION[{}]="{}"\n'.format(count,os.path.basename(path))]
    module_lines += ['DEST_MODULE_LOCATION[{}]="{}"\n'.format(count, os.path.join("/kernel/", path))]
    count += 1

lines += ['MAKE[0]="make {} -C /usr/src/linux-headers-{} M="/var/lib/dkms/hwmgmt/{}/build" KERNELDIR=/lib/modules/{}/build modules"\n'.format(cfg_opts, KVERSION, HWMGMT_VERSION, KVERSION)]
lines = lines + module_lines
lines += ['AUTOINSTALL="yes"\n']

with open("/usr/src/hwmgmt-{}/dkms.conf".format(HWMGMT_VERSION), "w") as conf:
    conf.writelines(lines)

MK = MK.format(" ".join(os.path.basename(path)+"/" for path in paths))
with open("/usr/src/hwmgmt-{}/Makefile".format(HWMGMT_VERSION), "w") as mk:
    mk.write(MK)

# Build
# subprocess.call("sudo dkms add hwmgmt/{}".format(HWMGMT_VERSION), shell=True)
# subprocess.call("sudo dkms build hwmgmt/{} -k {} -a {}".format(HWMGMT_VERSION, KVERSION, CONFIGURED_ARCH), shell=True)
# subprocess.call("sudo dkms mkbmdeb hwmgmt/{} -k {} -a {}".format(HWMGMT_VERSION, KVERSION, CONFIGURED_ARCH), shell=True)


# Copy resulting debs to expected location for Makefile
# TODO
