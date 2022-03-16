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

#
# Check auto configuration passed from boot-fifo
#
boot_fifo_path="/sys/bus/platform/devices/MLNXBF04:00/bootfifo"
if [ -e "${boot_fifo_path}" ]; then
	cfg_file=$(mktemp)
	# Get 16KB assuming it's big enough to hold the config file.
	dd if=${boot_fifo_path} of=${cfg_file} bs=4096 count=4

	#
	# Check the .xz signature {0xFD, '7', 'z', 'X', 'Z', 0x00} and extract the
	# config file from it. Then start decompression in the background.
	#
	offset=$(strings -a -t d ${cfg_file} | grep -m 1 "7zXZ" | awk '{print $1}')
	if [ -s "${cfg_file}" -a ."${offset}" != ."1" ]; then
		log "INFO: Found bf.cfg"
		cat ${cfg_file} | tr -d '\0' > /etc/bf.cfg
	fi
	rm -f $cfg_file
fi

if [ -e /etc/bf.cfg ]; then
	. /etc/bf.cfg
fi

# Read kernel cmdline parameters to check if logging is enabled
set -- $(cat /proc/cmdline)
for x in "$@"; do
    case "$x" in
        logging=true)
            DEBUG="yes"
            ;;
    esac
done

log_file=/sonic_install_log_file.log
if [ "X${DEBUG}" == "Xyes" ]; then
    touch $log_file
fi

ex(){
    if [ "X${DEBUG}" == "Xyes" ]; then
        # Execute the command and redirect the logs to the log file
        echo "COMMAND: $@" >> $log_file
        echo "STDOUT & STDERR:" >> $log_file
        "$@" >> $log_file 2>&1
        echo "EXT STATUS: $?" >> $log_file
        echo -e "\n" >> $log_file
    else
        "$@" > /dev/null 2>&1
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
ex blockdev --rereadpt ${device}

if function_exists bfb_pre_install; then
	bfb_pre_install
fi

# Generate some entropy
ex mke2fs  ${device}p2 >> /dev/null

ex mkdosfs ${device}p1 -n "system-boot"
ex mkfs.ext4 -F ${device}p2 -L "SONiC-OS"

ex fsck.vfat -a ${device}p1

mkdir -p /mnt
ex mount -t ext4 ${device}p2 /mnt
mkdir -p /mnt/boot/efi
ex mount -t vfat ${device}p1 /mnt/boot/efi

if [ "X${DEBUG}" == "Xyes" ]; then
    log "Extracting SONiC files"
fi

mkdir -p /mnt/$image_dir

# Extract the INSTALLER_PAYLOAD to the $image_dir
export EXTRACT_UNSAFE_SYMLINKS=1
ex unzip -o /debian/$INSTALLER_PAYLOAD -x $FILESYSTEM_DOCKERFS -d /mnt/$image_dir
mkdir -p /mnt/$image_dir/$DOCKERFS_DIR
unzip -op /debian/$INSTALLER_PAYLOAD "$FILESYSTEM_DOCKERFS" | tar xz --warning=no-timestamp -f - -C /mnt/$image_dir/$DOCKERFS_DIR

# Copy in the machine.conf file
cat <<EOF > /mnt/machine.conf
bf_vendor=nvidia
bf_machine=nvidia-bluefield
bf_arch=arm64
EOF

chmod a+r /mnt/machine.conf

sync

if [ "X${DEBUG}" == "Xyes" ]; then
    log "Installing GRUB"
fi

ex grub-install \
    --bootloader-id="SONiC-OS" \
    --efi-directory=/mnt/boot/efi/ \
    --boot-directory=/mnt/ \
    ${device}p1

# Create a minimal grub.cfg that allows for:
#   - configure the serial console
#   - allows for grub-reboot to work
#   - a menu entry for the DEMO OS

grub_cfg=$(mktemp)

# Modify GRUB_CMDLINE_LINUX from bf.cfg file if required
# GRUB_CMDLINE_LINUX

DEFAULT_GRUB_CMDLINE_LINUX="console=ttyAMA1 console=hvc0 console=ttyAMA0 earlycon=pl011,0x01000000 earlycon=pl011,0x01800000 quiet"
GRUB_CMDLINE_LINUX=${GRUB_CMDLINE_LINUX:-"$DEFAULT_GRUB_CMDLINE_LINUX"}
export GRUB_CMDLINE_LINUX

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
cat <<EOF >> $grub_cfg
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
        linux   /$image_dir/boot/vmlinuz-5.10.0-8-2-arm64 root=$grub_cfg_root rw $GRUB_CMDLINE_LINUX fixrtc \
                loop=$image_dir/$FILESYSTEM_SQUASHFS loopfstype=squashfs                       \
                systemd.unified_cgroup_hierarchy=0 \
                apparmor=1 security=apparmor varlog_size=4096 systemd.unified_cgroup_hierarchy=0 \
                isolcpus=1-7 nohz_full=1-7 rcu_nocbs=1-7
        echo    'Loading SONiC-OS initial ramdisk ...'
        initrd  /$image_dir/boot/initrd.img-5.10.0-8-2-arm64
}
EOF

# Copy the grub.cfg onto the boot-directory as specified in the grub-install
ex mkdir -p /mnt/grub 
ex cp $grub_cfg /mnt/grub/grub.cfg

sync

if [ "X${DEBUG}" == "Xyes" ]; then
    log "GRUB CFG Updated"
fi

# Update HW-dependant files
if (/usr/bin/lspci -n -d 15b3: | grep -wq 'a2d2'); then
    # BlueField-1
    if [ ! -n "$DHCP_CLASS_ID" ]; then
        DHCP_CLASS_ID="BF1Client"
    fi
elif (/usr/bin/lspci -n -d 15b3: | grep -wq 'a2d6'); then
    # BlueField-2
    if [ ! -n "$DHCP_CLASS_ID" ]; then
        DHCP_CLASS_ID="BF2Client"
    fi
fi

ex echo $DHCP_CLASS_ID

umount /mnt/boot/efi
umount /mnt

ex blockdev --rereadpt ${device}

ex fsck.vfat -a ${device}p1
sync

if [ -e /lib/firmware/mellanox/boot/capsule/update.cap ]; then
	ex bfrec --capsule /lib/firmware/mellanox/boot/capsule/update.cap
fi

ex bfbootmgr --cleanall

# Make it the boot partition
mounted_efivarfs=0
if [ ! -d /sys/firmware/efi/efivars ]; then
	ex mount -t efivarfs none /sys/firmware/efi/efivars
	mounted_efivarfs=1
fi

if efibootmgr | grep SONiC-OS; then
    ex efibootmgr -b "$(efibootmgr | grep SONiC-OS | cut -c 5-8)" -B
fi
ex efibootmgr -c -d "$device" -p 1 -L SONiC-OS -l "\EFI\SONiC-OS\grubaa64.efi"

if [ "X${DEBUG}" == "Xyes" ]; then
    log "EFIBootMgr Updated"
fi

BFCFG=`which bfcfg 2> /dev/null`
if [ -n "$BFCFG" ]; then
	# Create PXE boot entries
	# Not adding CX ifaces because presumably they'll not be used for PXE
	if [ -e /etc/bf.cfg ]; then
		mv /etc/bf.cfg /etc/bf.cfg.orig
	fi

	cat > /etc/bf.cfg << EOF
BOOT0=DISK
BOOT1=NET-OOB-IPV4
BOOT2=NET-OOB-IPV6
BOOT3=NET-RSHIM-IPV4
BOOT4=NET-RSHIM-IPV6
PXE_DHCP_CLASS_ID=$DHCP_CLASS_ID
EOF

	ex $BFCFG

	# Restore the original bf.cfg
	/bin/rm -f /etc/bf.cfg
	if [ -e /etc/bf.cfg.orig ]; then
		mv /etc/bf.cfg.orig /etc/bf.cfg
	fi
fi

if [ $mounted_efivarfs -eq 1 ]; then
	umount /sys/firmware/efi/efivars > /dev/null 2>&1
fi

if [ -n "$BFCFG" ]; then
	ex $BFCFG
fi

if function_exists bfb_post_install; then
	ex bfb_post_install
fi

if [ "X${DEBUG}" == "Xyes" ]; then
    # Copy the log file to Persistent Storage
    mount -t ext4 ${device}p2 /mnt
    mkdir -p /mnt/bfb-boot-logs/
    dmesg > /mnt/bfb-boot-logs/installer_bfb_dmesg.log
    mv $log_file /mnt/bfb-boot-logs/$log_file
    umount /mnt
    log "Rebooting..."
    log "Installation finished"
    # Wait for these messages to be pulled by the rshim service
    sleep 3
fi
