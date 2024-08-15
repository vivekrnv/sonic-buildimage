#!/bin/bash

# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Optimize Switch init by finishing tasks required for
# nvidia syncd that doesn't require database or swss
#

function check_warm_boot()
{
    SYSTEM_WARM_START=`sonic-db-cli STATE_DB hget "WARM_RESTART_ENABLE_TABLE|system" enable`
    SERVICE_WARM_START=`sonic-db-cli STATE_DB hget "WARM_RESTART_ENABLE_TABLE|syncd" enable`
    # SYSTEM_WARM_START could be empty, always make WARM_BOOT meaningful.
    if [[ x"$SYSTEM_WARM_START" == x"true" ]] || [[ x"$SERVICE_WARM_START" == x"true" ]]; then
        BOOT_WARM="true"
    else
        BOOT_WARM="false"
    fi
}

function check_fast_boot()
{
    SYSTEM_FAST_REBOOT=`sonic-db-cli STATE_DB hget "FAST_RESTART_ENABLE_TABLE|system" enable`
    if [[ x"${SYSTEM_FAST_REBOOT}" == x"true" ]]; then
        BOOT_FAST="true"
    else
        BOOT_FAST="false"
    fi
}


function GetMstDevice() {
    local _MST_DEVICE="$(ls /dev/mst/*_pci_cr0 2>&1)"

    if [[ ! -c "${_MST_DEVICE}" ]]; then
        echo "${UNKN_MST}"
    else
        echo "${_MST_DEVICE}"
    fi
}

function create_shared_storage() {
    rm -rf /tmp/nv-syncd-shared/
    mkdir -m 777 -p /tmp/nv-syncd-shared/
}

function debug()
{
    /usr/bin/logger $1
}

function start() {
    debug "Creating nvidia shared storage"
    create_shared_storage

    check_fast_boot
    check_warm_boot

    if [[ x"$BOOT_FAST" == x"true" || x"$BOOT_WARM" == x"true" ]]; then
        export FAST_BOOT=1
    fi

    debug "Starting Firmware update procedure"
    /usr/bin/mst start --with_i2cdev

    local -r _MST_DEVICE="$(GetMstDevice)"
    if [[ "${_MST_DEVICE}" != "${UNKN_MST}" ]]; then
        /usr/bin/flint -d $_MST_DEVICE --clear_semaphore
    fi

    /usr/bin/mlnx-fw-upgrade.sh -v
    if [[ "$?" -ne "0" ]]; then
        debug "Failed to upgrade fw. " "$?" "Restart syncd"
        exit 1
    fi

    /etc/init.d/sxdkernel restart
    debug "Firmware update procedure ended"
}

case "$1" in
    start)
        $1
        ;;
    *)
        echo "Usage: $0 {start}"
        exit 1
        ;;
esac

