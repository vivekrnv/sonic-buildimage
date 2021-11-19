#!/bin/bash

REPO="mellanox/bluefield"
TAG="bfb_builder_denian10-5.4-2.4.1.3-3.7.1.11866-1"

CDIR="/root/sonic/conf"
SDIR="/root/sonic"
DDIR="/sonic/"
TARGET_MACHINE=nvidia-bluefield

fail_with_cmd()
{
    echo $1
    exit 1
}

# Check if the image already exists 
docker image inspect $REPO:$TAG &> /dev/null
if [ $? -ne 0 ]; then
    echo "Image doesn't Exist, fetching $TAG from $REPO"
    docker pull $REPO:$TAG || fail_with_cmd "docker pull failed"
fi

. onie-image-arm64.conf

SONIC_VERSION=$(cat $FILESYSTEM_ROOT/etc/sonic/sonic_version.yml | grep build_version | cut -f2 -d" ")

echo "SONIC_VERSION: $SONIC_VERSION"

if [ ! -f "$ONIE_INSTALLER_PAYLOAD" ]; then
    echo "SONIC Related Payload '$ONIE_INSTALLER_PAYLOAD' is not found at $(pwd) exiting"
    exit 1
fi

docker run --privileged --init -e container=docker\
        -e "CDIR=$CDIR" -e "SDIR=$SDIR" -e "DDIR=$DDIR" \
        --mount type=bind,source="$(pwd)",target=/sonic \
        $REPO:$TAG \
        bash -c "mkdir -p $SDIR &&  
                 rm -rf $SDIR/* && 
                 mkdir -p $CDIR &&
                 cp /sonic/$ONIE_INSTALLER_PAYLOAD $CDIR &&
                 cp /sonic/onie-image-arm64.conf $CDIR &&
                 cp /sonic/installer/bluefield/create_sonic_bfb $SDIR &&
                 cp /sonic/installer/bluefield/install.sh $SDIR &&
                 cp /root/workspace/install.bfb $SDIR &&
                 ls $SDIR &&
                 /root/sonic/create_sonic_bfb -s $SONIC_VERSION" || fail_with_cmd "docker run failed"
                      
echo "Building BFB Finished"
exit 0
