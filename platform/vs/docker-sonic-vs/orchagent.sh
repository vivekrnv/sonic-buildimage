#!/usr/bin/env bash

#This is required since we have platform based checks in orchagent

if [ "$HWSKU" == "Mellanox-SN2700" ]; then
    export platform="mellanox"
else
    export platform=vs
fi

# Force orchagent to run with the given ASIC.
if [ "$ASIC_TYPE" == "broadcom-dnx" ]; then
    export platform="broadcom"
    export sub_platform="broadcom-dnx"
fi

# Allow test to override PfcDlrInitEnable for VS switch so that
# we can test PfcWdAclHandler, instead of PfcWdDlrHandler.
if [ "$PFC_DLR_INIT_ENABLE" == "1" ]; then
    export pfcDlrInitEnable="1"
elif [ "$PFC_DLR_INIT_ENABLE" == "0" ]; then
    export pfcDlrInitEnable="0"
fi

SWSS_VARS_FILE=/usr/share/sonic/templates/swss_vars.j2

# Retrieve SWSS vars from sonic-cfggen
SWSS_VARS=$(sonic-cfggen -d -y /etc/sonic/sonic_version.yml -t $SWSS_VARS_FILE) || exit 1

MAC_ADDRESS=$(echo $SWSS_VARS | jq -r '.mac')
if [ "$MAC_ADDRESS" == "None" ] || [ -z "$MAC_ADDRESS" ]; then
    MAC_ADDRESS=$(ip link show eth0 | grep ether | awk '{print $2}')
    logger "Mac address not found in Device Metadata, Falling back to eth0"
fi

# Create a folder for SwSS record files
mkdir -p /var/log/swss
ORCHAGENT_ARGS="-d /var/log/swss "

# Set orchagent pop batch size to 8192
ORCHAGENT_ARGS+="-b 8192 "

# Set synchronous mode if it is enabled in CONFIG_DB
SYNC_MODE=$(echo $SWSS_VARS | jq -r '.synchronous_mode')
if [ "$SYNC_MODE" == "enable" ]; then
    ORCHAGENT_ARGS+="-s "
fi

# Set mac address
ORCHAGENT_ARGS+="-m $MAC_ADDRESS"

exec /usr/bin/orchagent ${ORCHAGENT_ARGS}
