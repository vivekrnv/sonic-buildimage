#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
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

SUCCESS_CODE=0
RC=-1

if [[ -f "/usr/bin/asic_detect/asic_type" ]]; then
    cat /usr/bin/asic_detect/asic_type
    exit $SUCCESS_CODE
fi

# make sure that DEVICE_DICT keys are the same as values in DEVICE_ORDER
declare -A DEVICE_DICT=(
    ["cb84"]="spc1"
    ["cf6c"]="spc2"
    ["cf70"]="spc3"
    ["cf80"]="spc4"
    ["cf82"]="spc5"
    ["a2dc"]="bf3"
)
TYPE_UNKNOWN="unknown"
VENDOR_ID="15b3"
DEVICE_TYPE=$TYPE_UNKNOWN

# bf3 should be the last device in the list
DEVICE_ORDER=("cb84" "cf6c" "cf70" "cf80" "cf82" "a2dc")

lspci_output=$(lspci -n 2>/dev/null)
if [[ -n "$lspci_output" ]]; then
    for key in "${DEVICE_ORDER[@]}"; do
        if echo "$lspci_output" | grep "$VENDOR_ID:$key" &>/dev/null; then
            DEVICE_TYPE="${DEVICE_DICT[$key]}"
            RC=$SUCCESS_CODE
            break
        fi
    done
    if [[ -n "$DEVICE_TYPE" ]]; then
        echo "$DEVICE_TYPE" | tee >( [[ "$DEVICE_TYPE" != "$TYPE_UNKNOWN" ]] && cat > /usr/bin/asic_detect/asic_type )
    fi
    exit $RC
fi
