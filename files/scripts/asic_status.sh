#!/bin/bash

is_chassis_supervisor() {
    if [ -f /etc/sonic/chassisdb.conf ]; then
        true
        return
    fi
    false
    return
}

check_asic_status() {
    # Ignore services that are not started in namespace.
    if [[ -z $DEV ]]; then
        return 0
    fi

    # For chassis supervisor, wait for asic to be online
    /usr/local/bin/asic_status.py $SERVICE $DEV
    if [[ $? = 0 ]]; then
        debug "$SERVICE successfully detected asic $DEV..."
        return 0
    fi
    debug "$SERVICE failed to detect asic $DEV..."
    return 1
}
