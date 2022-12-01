#!/bin/bash

. /usr/local/bin/syncd_common.sh

function collect_saisdkdump() {
    TMP_DMP_DIR="/tmp/orch_abrt_sdkdump/"
    HOST_SDKDUMP_LOC="/var/log/orch_abrt_sdkdump/"
    local sai_dump_filename="sai_sdk_dump_$(date +"%m_%d_%Y_%I_%M_%p")"
    local sai_dump_filename_epoch="sai_sdk_dump_$(date +%s)"

    /usr/bin/docker exec syncd$DEV rm -rf ${TMP_DMP_DIR}
    /usr/bin/docker exec syncd$DEV rm -f /tmp/${sai_dump_filename_epoch}.tar
    /usr/bin/docker exec syncd$DEV mkdir -p ${TMP_DMP_DIR}
    timeout 30s bash -c "/usr/bin/docker exec syncd$DEV saisdkdump -f ${TMP_DMP_DIR}/${sai_dump_filename} > /dev/null"
    /usr/bin/docker exec syncd$DEV tar -czf /tmp/${sai_dump_filename_epoch}.tar.gz -C ${TMP_DMP_DIR} .

    if [[ $? == 0 ]]; then
        mkdir -p ${HOST_SDKDUMP_LOC}
        /usr/bin/docker cp syncd$DEV:/tmp/${sai_dump_filename_epoch}.tar.gz ${HOST_SDKDUMP_LOC}
        # Only retain the latest 10 files
        ls -1td ${HOST_SDKDUMP_LOC}/sai_sdk_dump_* | tail -n +10 | xargs rm -rf
        debug "${sai_dump_filename_epoch}.tar.gz collected before taking stopping syncd"
    else
        debug "Failed to collect saisdkdump before stopping syncd"
    fi
}

function startplatform() {

    # platform specific tasks

    # start mellanox drivers regardless of
    # boot type
    if [[ x"$sonic_asic_platform" == x"mellanox" ]]; then
        BOOT_TYPE=`getBootType`
        if [[ x"$WARM_BOOT" == x"true" || x"$BOOT_TYPE" == x"fast" ]]; then
            export FAST_BOOT=1
        fi

        if [[ x"$WARM_BOOT" != x"true" ]]; then
            if [[ x"$(/bin/systemctl is-active pmon)" == x"active" ]]; then
                /bin/systemctl stop pmon
                debug "pmon is active while syncd starting, stop it first"
            fi
        fi

        debug "Starting Firmware update procedure"
        /usr/bin/mst start --with_i2cdev
        /usr/bin/mlnx-fw-upgrade.sh
        /etc/init.d/sxdkernel restart
        debug "Firmware update procedure ended"
    fi

    if [[ x"$sonic_asic_platform" == x"barefoot" ]]; then
        is_usb0=$(ls /sys/class/net | grep usb0)
        if [[ "$is_usb0" == "usb0" ]]; then
            /usr/bin/ip link set usb0 down
            /usr/bin/ip link set usb0 up
        fi
    fi

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        if [ x$sonic_asic_platform == x'cavium' ]; then
            /etc/init.d/xpnet.sh start
        fi
    fi
}

function waitplatform() {

    BOOT_TYPE=`getBootType`
    if [[ x"$sonic_asic_platform" == x"mellanox" ]]; then
        if [[ x"$BOOT_TYPE" = @(x"fast"|x"warm"|x"fastfast") ]]; then
            PMON_TIMER_STATUS=$(systemctl is-active pmon.timer)
            if [[ x"$PMON_TIMER_STATUS" = x"inactive" ]]; then
                systemctl start pmon.timer
            else
                debug "PMON service is delayed by a timer for better fast/warm boot performance"
            fi
        else
            debug "Starting pmon service..."
            /bin/systemctl start pmon
            debug "Started pmon service"
        fi
    fi
    if [[ x"$BOOT_TYPE" = @(x"fast"|x"warm"|x"fastfast") ]]; then
        debug "LLDP service is delayed by a timer for better fast/warm boot performance"
    else
        lldp_state=$(systemctl is-enabled lldp.timer)
        if [[ $lldp_state == "enabled" ]]
        then
            debug "Starting lldp service..."
            /bin/systemctl start lldp
            debug "Started lldp service"
        fi
    fi
}

function stopplatform1() {

    if [[ x"$(${SONIC_DB_CLI} STATE_DB GET ORCH_ABRT_STATUS)" == x"1" ]]; then
        # Collecting saisdkdump before restarting syncd
        # Runs when orchagent is aborted because of SAI failure.
        # Only enabled for mellanox platform
        if [[ x$sonic_asic_platform == x"mellanox" ]]; then
            collect_saisdkdump
        fi
        # This is used to notify auto-techsupport process
        touch /tmp/saidump_collection_notify_flag
    fi

    if [[ x$sonic_asic_platform == x"mellanox" ]] && [[ x$TYPE == x"cold" ]]; then
        debug "Stopping pmon service ahead of syncd..."
        /bin/systemctl stop pmon
        debug "Stopped pmon service"
    fi

    if [[ x$sonic_asic_platform != x"mellanox" ]] || [[ x$TYPE != x"cold" ]]; then
        debug "${TYPE} shutdown syncd process ..."
        /usr/bin/docker exec -i syncd$DEV /usr/bin/syncd_request_shutdown --${TYPE}

        # wait until syncd quits gracefully or force syncd to exit after
        # waiting for 20 seconds
        start_in_secs=${SECONDS}
        end_in_secs=${SECONDS}
        timer_threshold=20
        while docker top syncd$DEV | grep -q /usr/bin/syncd \
                && [[ $((end_in_secs - start_in_secs)) -le $timer_threshold ]]; do
            sleep 0.1
            end_in_secs=${SECONDS}
        done

        if [[ $((end_in_secs - start_in_secs)) -gt $timer_threshold ]]; then
            debug "syncd process in container syncd$DEV did not exit gracefully"
        fi

        /usr/bin/docker exec -i syncd$DEV /bin/sync
        debug "Finished ${TYPE} shutdown syncd process ..."
    fi
}

function stopplatform2() {
    # platform specific tasks

    if [[ x"$WARM_BOOT" != x"true" ]]; then
        if [ x$sonic_asic_platform == x'mellanox' ]; then
            /etc/init.d/sxdkernel stop
            /usr/bin/mst stop
        elif [ x$sonic_asic_platform == x'cavium' ]; then
            /etc/init.d/xpnet.sh stop
            /etc/init.d/xpnet.sh start
        fi
    fi
}

OP=$1
DEV=$2

SERVICE="syncd"
PEER="swss"
DEBUGLOG="/tmp/swss-syncd-debug$DEV.log"
LOCKFILE="/tmp/swss-syncd-lock$DEV"
NAMESPACE_PREFIX="asic"
if [ "$DEV" ]; then
    NET_NS="$NAMESPACE_PREFIX$DEV" #name of the network namespace
    SONIC_DB_CLI="sonic-db-cli -n $NET_NS"
else
    NET_NS=""
    SONIC_DB_CLI="sonic-db-cli"
fi

case "$1" in
    start|wait|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|wait|stop}"
        exit 1
        ;;
esac
