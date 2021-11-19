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

# This script will run after being booted into a installer kernel 
# This will setup the disk, grub etc for the actual SONiC to boot from

# NOTE: Replace these flag at build time
IMAGE_VERSION="%%IMAGE_VERSION%%"
INSTALLER_PAYLOAD="%%INSTALLER_PAYLOAD%%"
FILESYSTEM_DOCKERFS="%%FILESYSTEM_DOCKERFS%%"
DOCKERFS_DIR="%%DOCKERFS_DIR%%"
FILESYSTEM_SQUASHFS="%%FILESYSTEM_SQUASHFS%%"

image_dir="image-$IMAGE_VERSION"
demo_volume_revision_label="SONiC-OS-${IMAGE_VERSION}"

PATH="/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/mellanox/scripts"
CHROOT_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

if [ -e /etc/bf.cfg ]; then
	. /etc/bf.cfg
fi

rshimlog=`which bfrshlog 2> /dev/null`
distro="SONiC"

log()
{
	if [ -n "$rshimlog" ]; then
		$rshimlog "$*"
	else
		echo "$*"
	fi
}

log "INFO: $distro installation started"

device=/dev/mmcblk0

# We cannot use wait-for-root as it expects the device to contain a
# known filesystem, which might not be the case here.
while [ ! -b $device ]; do
    printf "Waiting for %s to be ready\n" "$device"
    sleep 1
done

# Flash firmware from bfb to MMC device boot partitions (it alternates
# between boot0 and boot1, that is why we call mlx-bootctl twice).

# Update default.bfb
bfb_location=/lib/firmware/mellanox/default.bfb

if [ -f "$bfb_location" ]; then
	/bin/rm -f /mnt/lib/firmware/mellanox/boot/default.bfb
	mkdir -p /mnt/lib/firmware/mellanox/boot
	cp $bfb_location /mnt/lib/firmware/mellanox/boot/default.bfb
fi

# Update eMMC boot partitions. Update via either capsule
# path or default path (i.e., mlxbf-bootctl). This command
# MUST be executed after 'update_boot' and 'install_grub',
# otherwise the newly created boot option would be either
# cleaned up or unset from default option.
bfrec --policy dual
sleep 3

# Flash image
bs=512
reserved=34
boot_size_megs=50
mega=$((2**20))
boot_size_bytes=$(($boot_size_megs * $mega))

disk_sectors=`fdisk -l $device | grep "Disk $device:" | awk '{print $7}'`
disk_end=$((disk_sectors - reserved))

boot_start=2048
boot_size=$(($boot_size_bytes/$bs))
root_start=$((2048 + $boot_size))
root_end=$disk_end
root_size=$(($root_end - $root_start + 1))

dd if=/dev/zero of="$device" bs="$bs" count=1

sfdisk -f "$device" << EOF
label: gpt
label-id: A2DF9E70-6329-4679-9C1F-1DAF38AE25AE
device: ${device}
unit: sectors
first-lba: $reserved
last-lba: $disk_end

${device}p1 : start=$boot_start, size=$boot_size, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, uuid=CEAEF8AC-B559-4D83-ACB1-A4F45B26E7F0, name="EFI System", bootable
${device}p2 : start=$root_start ,size=$root_size, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, uuid=F093FF4B-CC26-408F-81F5-FF2DD6AE139F, name="SONiC-OS"
EOF

sync

# Refresh partition table
blockdev --rereadpt ${device} > /dev/null 2>&1

if function_exists bfb_pre_install; then
	bfb_pre_install
fi

# Generate some entropy
mke2fs  ${device}p2 >> /dev/null

mkdosfs ${device}p1 -n "system-boot"
mkfs.ext4 -F ${device}p2 -L "SONiC-OS"

fsck.vfat -a ${device}p1

mkdir -p /mnt
mount -t ext4 -o defaults,rw ${device}p2 /mnt
mkdir -p /mnt/boot/efi
mount -t vfat ${device}p1 /mnt/boot/efi

echo "Installing SONiC to /mnt/$image_dir"
mkdir -p /mnt/$image_dir

# Extract the INSTALLER_PAYLOAD to the $image_dir
export EXTRACT_UNSAFE_SYMLINKS=1
unzip -o /debian/$INSTALLER_PAYLOAD -x $FILESYSTEM_DOCKERFS -d /mnt/$image_dir
mkdir -p /mnt/$image_dir/$DOCKERFS_DIR
unzip -op /debian/$INSTALLER_PAYLOAD "$FILESYSTEM_DOCKERFS" | tar xz --warning=no-timestamp -f - -C /mnt/$image_dir/$DOCKERFS_DIR

# Copy in the machine.conf file
# TODO: Don't statically define bf_platform 
cat <<EOF > /mnt/machine.conf
bf_vendor=nvidia
bf_machine=nvidia-bluefield
bf_arch=arm64
EOF

chmod a+r /mnt/machine.conf

sync

if (grep -qE "MemTotal:\s+16" /proc/meminfo > /dev/null 2>&1); then
	echo "net.netfilter.nf_conntrack_max = 500000" > /mnt/usr/lib/sysctl.d/90-bluefield.conf
fi


umount /mnt/boot/efi
umount /mnt

blockdev --rereadpt ${device} > /dev/null 2>&1

fsck.vfat -a ${device}p1
sync

bfbootmgr --cleanall

# Make it the boot partition
mount -t efivarfs none /sys/firmware/efi/efivars
mount ${device}p2 /mnt/
mount ${device}p1 /mnt/boot/efi/

if [ -x /usr/sbin/grub-install ]; then
	grub-install \
		--bootloader-id="SONiC-OS" \
		--locale-directory=/mnt/usr/share/locale \
		--efi-directory=/mnt/boot/efi/ \
		--boot-directory=/mnt/ \
		${device}p1
else
	if efibootmgr | grep buster; then
		efibootmgr -b "$(efibootmgr | grep buster | cut -c 5-8)" -B
	fi
	efibootmgr -c -d "$device" -p 1 -L buster -l "\EFI\debian\grubaa64.efi"
fi

# Create a minimal grub.cfg that allows for:
#   - configure the serial console
#   - allows for grub-reboot to work
#   - a menu entry for the DEMO OS

grub_cfg=$(mktemp)

# Set a few GRUB_xxx environment variables that will be picked up and
# used by the 50_onie_grub script.  This is similiar to what an OS
# would specify in /etc/default/grub.
#
# GRUB_SERIAL_COMMAND
# GRUB_CMDLINE_LINUX
[ -r /debian/platform.conf ] && . /debian/platform.conf

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

# Add a menu entry for the SONiC OS
# Note: assume that apparmor is supported in the kernel
demo_grub_entry="$demo_volume_revision_label"

# Find the grub_cfg_root
uuid=$(blkid ${device}p2 | sed -ne 's/.* UUID=\"\([^"]*\)\".*/\1/p')
if [ -z "$uuid" ]; then
	grub_cfg_root=${device}p2
else
	grub_cfg_root=UUID=$uuid
fi

# Add common configuration, like the timeout
cat <<EOF > $grub_cfg
set timeout=5
EOF

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

# Copy the grub.cfg onto the boot-directory as specified in the grub-install
mkdir -p /mnt/grub && cp $grub_cfg /mnt/grub/grub.cfg

sync

umount /mnt/boot/efi
umount /mnt
umount /sys/firmware/efi/efivars

BFCFG=`which bfcfg 2> /dev/null`
if [ -n "$BFCFG" ]; then
	$BFCFG
fi

if function_exists bfb_post_install; then
	bfb_post_install
fi

log "INFO: Installation finished"
log "INFO: Rebooting..."
