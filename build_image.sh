#!/bin/bash
## This script is to generate an ONIE installer image based on a file system overload

## Enable debug output for script
set -x -e

## Read ONIE image related config file

CONFIGURED_ARCH=$([ -f .arch ] && cat .arch || echo amd64)
CONFIGURED_PLATFORM=$([ -f .platform ] && cat .platform || echo vs)

if [[ $CONFIGURED_ARCH == armhf || $CONFIGURED_ARCH == arm64 ]]; then
    . ./onie-image-${CONFIGURED_ARCH}.conf
else
    . ./onie-image.conf
fi

[ -n "$ONIE_IMAGE_PART_SIZE" ] || {
    echo "Error: Invalid ONIE_IMAGE_PART_SIZE in onie image config file"
    exit 1
}
[ -n "$ONIE_INSTALLER_PAYLOAD" ] || {
    echo "Error: Invalid ONIE_INSTALLER_PAYLOAD in onie image config file"
    exit 1
}

IMAGE_VERSION="${SONIC_IMAGE_VERSION}"

generate_kvm_image()
{
    NUM_ASIC=$1
    if [ $NUM_ASIC == 4 ]; then
         KVM_IMAGE=$OUTPUT_KVM_4ASIC_IMAGE
         RECOVERY_ISO=$onie_recovery_kvm_4asic_image
    elif [ $NUM_ASIC == 6 ]; then
         KVM_IMAGE=$OUTPUT_KVM_6ASIC_IMAGE
         RECOVERY_ISO=$onie_recovery_kvm_6asic_image
    else
         KVM_IMAGE=$OUTPUT_KVM_IMAGE
         RECOVERY_ISO=$onie_recovery_image
         NUM_ASIC=1
    fi

    echo "Build $NUM_ASIC-asic KVM image"
    KVM_IMAGE_DISK=${KVM_IMAGE%.gz}
    sudo rm -f $KVM_IMAGE_DISK $KVM_IMAGE_DISK.gz

    SONIC_USERNAME=$USERNAME PASSWD=$PASSWORD sudo -E ./scripts/build_kvm_image.sh $KVM_IMAGE_DISK $RECOVERY_ISO $OUTPUT_ONIE_IMAGE $KVM_IMAGE_DISK_SIZE

    if [ $? -ne 0 ]; then
        echo "Error : build kvm image failed"
        exit 1
    fi

    [ -r $KVM_IMAGE_DISK ] || {
        echo "Error : $KVM_IMAGE_DISK not generated!"
        exit 1
    }

    gzip $KVM_IMAGE_DISK

    [ -r $KVM_IMAGE_DISK.gz ] || {
        echo "Error : gzip $KVM_IMAGE_DISK failed!"
        exit 1
    }

    echo "The compressed kvm image is in $KVM_IMAGE_DISK.gz"
}

generate_onie_installer_image()
{
    # Copy platform-specific ONIE installer config files where onie-mk-demo.sh expects them
    rm -rf ./installer/x86_64/platforms/
    mkdir -p ./installer/x86_64/platforms/
    for VENDOR in `ls ./device`; do
        for PLATFORM in `ls ./device/$VENDOR`; do
            if [ -f ./device/$VENDOR/$PLATFORM/installer.conf ]; then
                cp ./device/$VENDOR/$PLATFORM/installer.conf ./installer/x86_64/platforms/$PLATFORM
            fi

        done
    done

    ## Generate an ONIE installer image
    ## Note: Don't leave blank between lines. It is single line command.
    ./onie-mk-demo.sh $TARGET_PLATFORM $TARGET_MACHINE $TARGET_PLATFORM-$TARGET_MACHINE-$ONIEIMAGE_VERSION \
          installer platform/$TARGET_MACHINE/platform.conf $OUTPUT_ONIE_IMAGE OS $IMAGE_VERSION $ONIE_IMAGE_PART_SIZE \
          $ONIE_INSTALLER_PAYLOAD
}

# Generate asic-specific device list
generate_device_list()
{
    local platforms_asic=$1

    # Create an empty function, and later append to it
    echo -n > $platforms_asic

    for d in `find -L ./device  -maxdepth 2 -mindepth 2 -type d`; do
        if [ -f $d/platform_asic ]; then
            if [ "$CONFIGURED_PLATFORM" = "generic" ] || grep -Fxq "$CONFIGURED_PLATFORM" $d/platform_asic; then
                echo "${d##*/}" >> "$platforms_asic";
            fi;
        fi;
    done
}

clean_dir()
{
    rm -rf $1
    exit $2
}

generate_s2s_installer_image_bluefield()
{
    if  [ ! -d installer ] || [ ! -r installer/sharch_body.sh ] ; then
        echo "Error: Invalid installer script directory: installer"
        exit 1
    fi

    if  [ ! -d installer/bluefield ] || [ ! -r installer/bluefield/sonic_to_sonic.sh ] ; then
        echo "Error: Invalid arch installer directory: installer/bluefield"
        exit 1
    fi

    # Copy platform-specific installer config files
    rm -rf ./installer/bluefield/platforms/
    mkdir -p ./installer/bluefield/platforms/
    for PLATFORM in `ls ./device/nvidia-bluefield`; do
        if [ -f ./device/nvidia-bluefield/$PLATFORM/installer.conf ]; then
            cp ./device/nvidia-bluefield/$PLATFORM/installer.conf ./installer/bluefield/platforms/$PLATFORM
        fi
    done

    echo -n "Building self-extracting install image ."
    tmp_dir=$(mktemp --directory)
    tmp_installdir="$tmp_dir/installer"
    mkdir $tmp_installdir || clean_dir $tmp_dir 1

    # Copy the bluefield specific sonic_to_sonic installer script and rename
    cp installer/bluefield/sonic_to_sonic.sh $tmp_installdir/install.sh

    # Replace the build time flags inside the script
    sed -i -e "s/%%IMAGE_VERSION%%/$IMAGE_VERSION/g" \
           -e "s/%%INSTALLER_PAYLOAD%%/$ONIE_INSTALLER_PAYLOAD/g" \
           -e "s/%%FILESYSTEM_DOCKERFS%%/$FILESYSTEM_DOCKERFS/g" \
           -e "s/%%DOCKERFS_DIR%%/$DOCKERFS_DIR/g" \
           -e "s/%%FILESYSTEM_SQUASHFS%%/$FILESYSTEM_SQUASHFS/g" \
           -e "s/%%KERNEL_VERSION%%/$KVERSION/g" $tmp_installdir/install.sh || clean_dir $tmp_dir 1
    chmod 0755 $tmp_installdir/install.sh

    # Copy the payload file
    cp $ONIE_INSTALLER_PAYLOAD $tmp_installdir || clean_dir  $tmp_dir 1

    # Create machine.conf file
    echo "machine=nvidia-bluefield" > $tmp_installdir/machine.conf
    echo "platform=arm64" >> $tmp_installdir/machine.conf

    sharch="$tmp_dir/sharch.tar"
    tar -C $tmp_dir -cf $sharch installer || {
        echo "Error: Problems creating $sharch archive"
        clean_dir $tmp_dir 1
    }

    [ -f "$sharch" ] || {
        echo "Error: $sharch not found"
        clean_dir $tmp_dir 1
    }

    sha1=$(cat $sharch | sha1sum | awk '{print $1}')
    echo -n "."

    cp installer/sharch_body.sh $OUTPUT_ONIE_IMAGE || {
        echo "Error: Problems copying sharch_body.sh"
        clean_dir 1
    }

    # Replace variables in the sharch template
    sed -i -e "s/%%IMAGE_SHA1%%/$sha1/" $OUTPUT_ONIE_IMAGE
    echo -n "."
    cat $sharch >> $OUTPUT_ONIE_IMAGE
    rm -rf $tmp_dir
    echo " Done."

    echo "Success:  Demo install image is ready in ${OUTPUT_ONIE_IMAGE}:"

    clean_dir $tmp_dir  0
}

if [ "$IMAGE_TYPE" = "onie" ]; then
    echo "Build ONIE installer"
    mkdir -p `dirname $OUTPUT_ONIE_IMAGE`
    sudo rm -f $OUTPUT_ONIE_IMAGE

    generate_device_list "./installer/$TARGET_PLATFORM/platforms_asic"

    generate_onie_installer_image
## Build a raw partition dump image using the ONIE installer that can be
## used to dd' in-lieu of using the onie-nos-installer. Used while migrating
## into SONiC from other NOS.
elif [ "$IMAGE_TYPE" = "raw" ]; then

    echo "Build RAW image"
    mkdir -p `dirname $OUTPUT_RAW_IMAGE`
    sudo rm -f $OUTPUT_RAW_IMAGE

    generate_device_list "./installer/$TARGET_PLATFORM/platforms_asic"

    generate_onie_installer_image

    echo "Creating SONiC raw partition : $OUTPUT_RAW_IMAGE of size $RAW_IMAGE_DISK_SIZE MB"
    fallocate -l "$RAW_IMAGE_DISK_SIZE"M $OUTPUT_RAW_IMAGE

    # ensure proc is mounted
    sudo mount proc /proc -t proc || true

    ## Generate a partition dump that can be used to 'dd' in-lieu of using the onie-nos-installer
    ## Run the installer
    ## The 'build' install mode of the installer is used to generate this dump.
    sudo chmod a+x $OUTPUT_ONIE_IMAGE
    sudo ./$OUTPUT_ONIE_IMAGE

    [ -r $OUTPUT_RAW_IMAGE ] || {
        echo "Error : $OUTPUT_RAW_IMAGE not generated!"
        exit 1
    }

    gzip $OUTPUT_RAW_IMAGE

    [ -r $OUTPUT_RAW_IMAGE.gz ] || {
        echo "Error : gzip $OUTPUT_RAW_IMAGE failed!"
        exit 1
    }

    mv $OUTPUT_RAW_IMAGE.gz $OUTPUT_RAW_IMAGE
    echo "The compressed raw image is in $OUTPUT_RAW_IMAGE"

elif [ "$IMAGE_TYPE" = "kvm" ]; then

    generate_device_list "./installer/$TARGET_PLATFORM/platforms_asic"

    generate_onie_installer_image
    # Generate single asic KVM image
    generate_kvm_image
    if [ "$BUILD_MULTIASIC_KVM" == "y" ]; then
        # Genrate 4-asic KVM image
        generate_kvm_image 4
        # Generate 6-asic KVM image
        generate_kvm_image 6
    fi


## Use 'aboot' as target machine category which includes Aboot as bootloader
elif [ "$IMAGE_TYPE" = "aboot" ]; then
    echo "Build Aboot installer"
    mkdir -p `dirname $OUTPUT_ABOOT_IMAGE`
    sudo rm -f $OUTPUT_ABOOT_IMAGE
    sudo rm -f $ABOOT_BOOT_IMAGE
    ## Add main payload
    cp $ONIE_INSTALLER_PAYLOAD $OUTPUT_ABOOT_IMAGE
    ## Add Aboot boot0 file
    j2 -f env files/Aboot/boot0.j2 ./onie-image.conf > files/Aboot/boot0
    sed -i -e "s/%%IMAGE_VERSION%%/$IMAGE_VERSION/g" files/Aboot/boot0
    pushd files/Aboot && zip -g $OLDPWD/$OUTPUT_ABOOT_IMAGE boot0; popd
    pushd files/Aboot && zip -g $OLDPWD/$ABOOT_BOOT_IMAGE boot0; popd
    pushd files/image_config/secureboot && zip -g $OLDPWD/$OUTPUT_ABOOT_IMAGE allowlist_paths.conf; popd
    echo "$IMAGE_VERSION" >> .imagehash
    zip -g $OUTPUT_ABOOT_IMAGE .imagehash
    zip -g $ABOOT_BOOT_IMAGE .imagehash
    rm .imagehash
    echo "SWI_VERSION=42.0.0" > version
    echo "SWI_MAX_HWEPOCH=2" >> version
    echo "SWI_VARIANT=US" >> version
    zip -g $OUTPUT_ABOOT_IMAGE version
    zip -g $ABOOT_BOOT_IMAGE version
    rm version

    generate_device_list ".platforms_asic"
    zip -g $OUTPUT_ABOOT_IMAGE .platforms_asic

    zip -g $OUTPUT_ABOOT_IMAGE $ABOOT_BOOT_IMAGE
    rm $ABOOT_BOOT_IMAGE
    if [ "$SONIC_ENABLE_IMAGE_SIGNATURE" = "y" ]; then
        TARGET_CA_CERT="$TARGET_PATH/ca.cert"
        rm -f "$TARGET_CA_CERT"
        [ -f "$CA_CERT" ] && cp "$CA_CERT" "$TARGET_CA_CERT"
        ./scripts/sign_image.sh -i "$OUTPUT_ABOOT_IMAGE" -k "$SIGNING_KEY" -c "$SIGNING_CERT" -a "$TARGET_CA_CERT"
    fi

elif [[ $IMAGE_TYPE = s2s && $CONFIGURED_PLATFORM == nvidia-bluefield ]]; then
    # bluefield Doesn't have ONiE Support yet and this *.bin image generated can only be used for SONiC-SONiC installation
    echo "Build SONiC to SONiC installer for Bluefield"
    mkdir -p `dirname $OUTPUT_ONIE_IMAGE`
    sudo rm -f $OUTPUT_ONIE_IMAGE
    generate_s2s_installer_image_bluefield

elif [[ ( $IMAGE_TYPE == bfb || $IMAGE_TYPE == pxe ) && $CONFIGURED_PLATFORM == nvidia-bluefield ]]; then
    sudo --preserve-env /sonic/installer/bluefield/create_sonic_image --kernel $KVERSION
    sudo chown $USER ./$OUTPUT_BFB_IMAGE
    if [[ $IMAGE_TYPE == pxe ]]; then
        sudo chown $USER ./$OUTPUT_PXE_IMAGE
    fi
else
    echo "Error: Non supported image type $IMAGE_TYPE"
    exit 1
fi
