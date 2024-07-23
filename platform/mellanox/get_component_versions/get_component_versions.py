#!/usr/bin/env python3
#
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
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

import os
import subprocess
import re

try:
    from fwutil.lib import PlatformDataProvider
except Exception:
    PlatformDataProvider = None

from sonic_py_common.general import check_output_pipe
from sonic_platform.device_data import DeviceDataManager
from tabulate import tabulate

COMPONENT_VERSIONS_FILE = "/etc/mlnx/component-versions"
HEADERS = ["COMPONENT", "COMPILATION", "ACTUAL"]
COMMANDS_FOR_ACTUAL = {
    "MFT": [["dpkg", "-l"], ["grep", "mft "], "mft *([0-9.-]*)"],
    "HW_MANAGEMENT": [["dpkg", "-l"], ["grep", "hw"], ".*1\\.mlnx\\.([0-9.]*)"],
    "SDK": [["docker", "exec", "-it", "syncd", "bash", "-c", 'dpkg -l | grep sdk'], ".*1\\.mlnx\\.([0-9.]*)"],
    "SAI": [["docker", "exec", "-it", "syncd", "bash", "-c", 'dpkg -l | grep mlnx-sai'], ".*1\\.mlnx\\.([A-Za-z0-9.]*)"],
    "FW": [["mlxfwmanager", "--query"], "FW * [0-9]{2}\\.([0-9.]*)"],
    "KERNEL": [["uname", "-r"], "([0-9][0-9.-]*)-.*"]
}

UNAVAILABLE_PLATFORM_VERSIONS = {
    "ONIE": "N/A",
    "SSD": "N/A",
    "BIOS": "N/A",
    "CPLD": "N/A"
}

UNAVAILABLE_COMPILED_VERSIONS = {
    "SDK": "N/A",
    "FW": "N/A",
    "SAI": "N/A",
    "HW_MANAGEMENT": "N/A",
    "MFT": "N/A",
    "KERNEL": "N/A"
}


def parse_compiled_components_file():
    compiled_versions = UNAVAILABLE_COMPILED_VERSIONS

    if not os.path.exists(COMPONENT_VERSIONS_FILE):
        return UNAVAILABLE_COMPILED_VERSIONS

    with open(COMPONENT_VERSIONS_FILE, 'r') as component_versions:
        for line in component_versions.readlines():
            try:
                comp, version = line.split()
                compiled_versions[comp] = version
            except ValueError:
                continue 

    return compiled_versions


def get_platform_component_versions():
    ccm = None
    
    if PlatformDataProvider:
        pdp = PlatformDataProvider()
        ccm = pdp.chassis_component_map

    if not ccm:
        return UNAVAILABLE_PLATFORM_VERSIONS

    versions_map = None

    # The first layer of the map only has one item
    for key, value in ccm.items():
        versions_map = value
        break

    if not versions_map or len(versions_map) == 0:
        return UNAVAILABLE_PLATFORM_VERSIONS

    platform_versions = {}
    for component_name, component in versions_map.items():
        platform_versions[component_name] = component.get_firmware_version()

    return platform_versions


def get_current_version(comp):
    version = ""
    try:
        # If there's only one command
        if len(COMMANDS_FOR_ACTUAL[comp]) == 2:
            version = subprocess.run(COMMANDS_FOR_ACTUAL[comp][0], shell=False, stdout=subprocess.PIPE, text=True)
            version = str(version.stdout)
        #If there are two commands and we need a pipe
        elif len(COMMANDS_FOR_ACTUAL[comp]) == 3:
            version = check_output_pipe(COMMANDS_FOR_ACTUAL[comp][0], COMMANDS_FOR_ACTUAL[comp][1])
        parsed_version = re.search(COMMANDS_FOR_ACTUAL[comp][-1], version)
        return parsed_version.group(1) if parsed_version else "N/A"
    except Exception:
        return "N/A"


def format_output_table(table):
    return tabulate(table, HEADERS)


def main():

    if os.getuid() != 0:
        print("Error: Root privileges are required")
        return

    compiled_versions = parse_compiled_components_file()
    simx_compiled_ver = compiled_versions.pop("SIMX")

    # Add compiled versions to table
    output_table = []
    for comp in compiled_versions.keys():
        actual = get_current_version(comp)
        output_table.append([comp, compiled_versions[comp], actual])

    # Handle if SIMX
    if DeviceDataManager.is_simx_platform():
        simx_actual_ver = DeviceDataManager.get_simx_version()
        output_table.append(["SIMX", simx_compiled_ver, simx_actual_ver])
        platform_versions = UNAVAILABLE_PLATFORM_VERSIONS
    else:
        platform_versions = get_platform_component_versions()

    # Add actual versions to table
    for comp in platform_versions.keys():
        output_table.append([comp, "-", platform_versions[comp]])

    print(format_output_table(output_table))


if __name__ == "__main__":
    main()
