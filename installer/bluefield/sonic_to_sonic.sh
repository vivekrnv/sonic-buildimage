#!/bin/bash
#
# Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES.
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


# This script is run on the Bluefield already running SONiC

set -e

# NOTE: Replace these flag at build time
IMAGE_VERSION="%%IMAGE_VERSION%%"
INSTALLER_PAYLOAD="%%INSTALLER_PAYLOAD%%"
FILESYSTEM_DOCKERFS="%%FILESYSTEM_DOCKERFS%%"
DOCKERFS_DIR="%%DOCKERFS_DIR%%"
FILESYSTEM_SQUASHFS="%%FILESYSTEM_SQUASHFS%%"

image_version="%%IMAGE_VERSION%%"
image_dir="image-$IMAGE_VERSION"
demo_volume_revision_label="SONiC-OS-${IMAGE_VERSION}"

cd $(dirname $0)
if [ -r ./machine.conf ]; then
    . ./machine.conf
fi

echo "SONiC-SONiC Installer: platform: $platform"

# Make sure run as root or under 'sudo'
if [ $(id -u) -ne 0 ]
    then echo "Please run as root"
    exit 1
fi

if [ -r /etc/machine.conf ]; then
    . /etc/machine.conf
elif [ -r /host/machine.conf ]; then
    . /host/machine.conf
fi

# Get platform specific linux kernel command line arguments
ONIE_PLATFORM_EXTRA_CMDLINE_LINUX=""

# Default var/log device size in MB
VAR_LOG_SIZE=4096

demo_mnt="/host"
# Get current SONiC image (grub/aboot/uboot)
eval running_sonic_revision="$(cat /proc/cmdline | sed -n 's/^.*loop=\/*image-\(\S\+\)\/.*$/\1/p')"
# Verify SONiC image exists
if [ ! -d "$demo_mnt/image-$running_sonic_revision" ]; then
    echo "ERROR: SONiC installation is corrupted: path $demo_mnt/image-$running_sonic_revision doesn't exist"
    exit 1
fi
# Prevent installing existing SONiC if it is running
if [ "$image_dir" = "image-$running_sonic_revision" ]; then
    echo "Not installing SONiC version $running_sonic_revision, as current running SONiC has the same version"
    exit 0
fi
# Remove extra SONiC images if any
for f in $demo_mnt/image-* ; do
    if [ -d $f ] && [ "$f" != "$demo_mnt/image-$running_sonic_revision" ] && [ "$f" != "$demo_mnt/$image_dir" ]; then
        echo "Removing old SONiC installation $f"
        rm -rf $f
    fi
done

# Create target directory or clean it up if exists
if [ -d $demo_mnt/$image_dir ]; then
    echo "Directory $demo_mnt/$image_dir/ already exists. Cleaning up..."
    rm -rf $demo_mnt/$image_dir/*
else
    mkdir $demo_mnt/$image_dir || {
        echo "Error: Unable to create SONiC directory"
        exit 1
    }
fi

# Decompress the file for the file system directly to the partition
if [ x"$docker_inram" = x"on" ]; then
    # when disk is small, keep dockerfs.tar.gz in disk, expand it into ramfs during initrd
    unzip -o $INSTALLER_PAYLOAD -d $demo_mnt/$image_dir
else
    unzip -o $INSTALLER_PAYLOAD -x "$FILESYSTEM_DOCKERFS" -d $demo_mnt/$image_dir

    TAR_EXTRA_OPTION="--numeric-owner --warning=no-timestamp"
    mkdir -p $demo_mnt/$image_dir/$DOCKERFS_DIR
    unzip -op $INSTALLER_PAYLOAD "$FILESYSTEM_DOCKERFS" | tar xz $TAR_EXTRA_OPTION -f - -C $demo_mnt/$image_dir/$DOCKERFS_DIR
fi


# Edit the grub parameters
demo_grub_entry="$demo_volume_revision_label"

old_sonic_menuentry=$(cat /host/grub/grub.cfg | sed "/$running_sonic_revision/,/}/!d")

# Find the grub_cfg_root
device=/dev/mmcblk0
uuid=$(blkid ${device}p2 | sed -ne 's/.* UUID=\"\([^"]*\)\".*/\1/p')
if [ -z "$uuid" ]; then
	grub_cfg_root=${device}p2
else
	grub_cfg_root=UUID=$uuid
fi

grub_cfg=$(mktemp)
# Add common configuration, like the timeout
cat <<EOF > $grub_cfg
set timeout=5

EOF

# Add the logic to support grub-reboot and grub-set-default
cat <<EOF >> $grub_cfg
if [ -s \$prefix/grubenv ]; then
    load_env
fi
if [ "\${saved_entry}" ]; then
    set default="\${saved_entry}"
fi
if [ "\${next_entry}" ]; then
    set default="\${next_entry}"
    unset next_entry
    save_env next_entry
fi

EOF

# Add the next-boot entry
cat <<EOF >> $grub_cfg
menuentry '$demo_grub_entry' {
        insmod gzio
        insmod part_gpt
        insmod ext2
        search --no-floppy --label --set=root SONiC-OS
        if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
        echo 'Loading SONiC-OS Kernel'
        linux   /$image_dir/boot/vmlinuz-4.19.0-12-2-arm64 root=$grub_cfg_root rw console=ttyAMA1 console=hvc0 console=ttyAMA0 earlycon=pl011,0x01000000 earlycon=pl011,0x01800000 fixrtc \
                loop=$image_dir/$FILESYSTEM_SQUASHFS loopfstype=squashfs                       \
                systemd.unified_cgroup_hierarchy=0 \
                apparmor=1 security=apparmor varlog_size=4096 systemd.unified_cgroup_hierarchy=0
        echo    'Loading SONiC-OS initial ramdisk ...'
        initrd  /$image_dir/boot/initrd.img-4.19.0-12-2-arm64
}

EOF

cat <<EOF >> $grub_cfg
$old_sonic_menuentry
EOF

cp $grub_cfg $demo_mnt/grub/grub.cfg

cd /

echo "Installed SONiC base image $demo_volume_label successfully"
