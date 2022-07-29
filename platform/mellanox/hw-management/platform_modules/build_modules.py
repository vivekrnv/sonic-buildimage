import os
import subprocess

LINUX="5.10.43"
HWMGMT_VERSION="7.5.1300"
CONFIGURED_ARCH="amd64"
KVERSION="5.10.42"

def find_module(obj, var):
    for v, o in var.items():
        if obj in o:
            if v.endswith("-objs"):
                return find_module("{}.o".format(v.replace("-objs","")), var)
            else:
                return o[0].replace(".o","")
    return None # Fail to find module


# Get list of patches from hw-mgmt
patchpath = "../hw-mgmt/recipes-kernel/linux/linux-5.10/"
patches = [f for f in os.listdir(patchpath) if f.endswith(".patch")]
patches = [os.path.join(patchpath, f) for f in patches]
patches.sort()

# Get ignored patches and remove from patch set
ignore = []
with open("ignored-patches") as im:
    ignore = im.readlines()
for i in ignore:
    try:
        patches.remove([p for p in patches if i.strip() == os.path.basename(p)][0])
    except ValueError:
        print("WARNING Ignored patch {} not included in hw-mgmt patch set.".format(i))

with open(os.path.join(patchpath, "series"), "w") as s:
    s.writelines(["{}\n".format(os.path.basename(p)) for p in patches])

# Get list of patches from SONiC
sonicpath = "../../../../src/sonic-linux-kernel/patch"
sonicpatch = [f[0:8] for f in os.listdir(sonicpath) if f.endswith(".patch")]

# Download and unpack kernel (check if this kernel is present in sonic-linux-kernel)
linux_tar = "linux-{}.tar.gz".format(LINUX)
sonic_linux_kernel = os.path.join("../../../../src/sonic-linux-kernel", linux_tar)
if os.path.exists(sonic_linux_kernel):
    shutil.copy(sonic_linux_kernel, linux_tar)
else:
    subprocess.call("wget -nc https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-{}.tar.gz".format(LINUX), shell=True)

subprocess.call("rm -rf linux-{}".format(LINUX), shell=True)
subprocess.call("tar xf {}".format(linux_tar), shell=True)
subprocess.call("git init; git add -A; git commit -m 'Init'; stg init; stg import -s {}".format(os.path.join("..", patchpath, "series")), 
        shell=True, cwd="linux-{}".format(LINUX))

# Apply patches
#for p in patches:
#    subprocess.call("git am {}".format(os.path.join("..", p)), shell=True, cwd="linux-{}".format(LINUX))

# Get a list of modified files from hw-mgmt patches
fl = {p:[o.split(' ')[1].replace('b/', '')
            for o in subprocess.check_output("grep -h '+++ .*\.c' {} || true".format(p), shell=True).decode("UTF-8").split('\n')
            if "+++" in o] 
            for p in patches}

# Locate and parse Makefile for each c file to get module name
mods = {}
mod_map = {}
no_mods = []
for p, files in fl.items():
    for f in files:
        makefile = os.path.join(os.path.join("linux-{}".format(LINUX), os.path.dirname(f)),"Makefile")

        if not os.path.exists(makefile):
            no_mods += [p]
            continue

        var = {}
        with open(makefile) as mf:

            # Collapse multi-line statements
            lines = []
            curr = ""
            for l in mf.readlines():
                curr += l.strip().replace('\n','').replace('\\', '')
                if not l.strip().endswith('\\'):
                    lines += [curr]
                    curr = ""

            # Parse variable assignments
            for l in lines:
                if '=' not in l: continue # skip if not assignment

                if '+=' in l: sep = '+=' # check the type of assignment
                elif ':=' in l: sep = ':='
                else: sep = '='

                name = l.split(sep)[0].strip()
                val = l.split(sep)[1].strip()

                objs = [t for o in val.split(' ') for t in o.split('\t') if t != ''] # Split for both spaces and tabs

                key = name.replace('\t','').replace(' ','') # remove whitepsace from key
                if key in var:
                    var[key] += objs
                else:
                    var[key] = objs

            # Determine module name
            obj_name = os.path.basename(f).replace('.c', '.o')
            mod = find_module(obj_name, var)

            # Add module name to mods set and mod_map dict. Record if no module found
            if mod is None:
                no_mods += [p]
            else:
                mods[mod] = os.path.dirname(f)
                if mod in mod_map.keys():
                    mod_map[p].append(mod)
                else:
                    mod_map[p] = [mod]


# Get overriden modules
override = []
with open("override-modules") as om:
    override = om.readlines()

# Get included patches (patches we are waiving checks for but want to include, these are mostly header patches we can't map modules to)
included = []
with open("included-patches") as inc:
    included = inc.readlines()

# Verify all patches are loaded in
# Make sure if we are loading a patch through DKMS that all modules for that patch successfully resolved
# Make sure if we are not loading a patch through DKMS that it is present in sonic-linux-kernel
error = False
msg = ""
for p, f in fl.items():
    if os.path.basename(p)[0:8] not in sonicpatch and os.path.basename(p) not in ignore and os.path.basename(p) not in included:
        if len(f) == 0:
            error = True
            msg += "Patch has no changed files: {}\n".format(p)
            continue
        if p in no_mods:
            error = True
            msg += "Unable to locate modules for patch {}.\n".format(p)
            continue
        if p in mod_map.keys():
            for m in mod_map[p]:
                if m not in override:
                    error = True
                    msg += "Module {} required for patch {}\n".format(m,p)
        else:
            error = True
            msg += "Patch {} not in modules or upstream kernel!\n".format(p)
if error: raise ValueError(msg)



# Build overriden modules (explore combining all of these into single package)

os.mkdir("/usr/src/hwmgmt-{}".format(HWMGMT_VERSION))
with open("/usr/src/hwmgmt-{}/dkms.conf".format(HWMGMT_VERSION), "w") as conf:
    lines = []
    lines += ['PACKAGE_NAME="hwmgmt"i\n']
    lines += ['PACKAGE_VERSION="{}"\n'.format(HWMGMT_VERSION)]

    count = 0
    for mod, path in mods.items():
        if mod in override:
            shutil.move(os.path.join("linux-{}".format(LINUX),path), "/usr/src/hwmgmt-{}/{}".format(HWMGMT_VERSION, mod)) # Move to correct folder
            lines += ['BUILT_MODULE_NAME[{}]="{}"\n'.format(count,mod)]
            lines ++ ['BUILT_MODULE_LOCATION[{}]="{}/"\n'.format(count,mod)]
            lines += ['DEST_MODULE_LOCATION[{}]="{}"\n'.format(count, os.path.join("/kernel/", path))]
            lines += ['MAKE[{}]="make -C {}/ KERNELDIR=/lib/modules/${kernelver}/build"\n'.format(count,mod)]
            count += 1


    lines += ['AUTOINSTALL="yes"\n']
    conf.writelines(lines)


quit()

# Build
subprocess.call("sudo dkms add hwmgmt/{}".format(HWMGMT_VERSION))
subprocess.call("sudo dkms build hwmgmt/{} -k {} -a {}".format(HWMGMT_VERSION, KVERSION, CONFIGURED_ARCH))
subprocess.call("sudo mkbmdeb build hwmmgt/{} -k {} -a {}".format(HWMGMT_VERSION, KVERSION, CONFIGURED_ARCH))


# Copy resulting debs to expected location for Makefile
# TODO
