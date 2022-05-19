#!/bin/bash
#
# Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES.
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

start()
{
    modprobe mlx5_core

    # NOTE: temporary workaround. SDN application requires to have interfaces up
    # and have IP addresses configured.
    sleep 2
    ifconfig p0 up
    ifconfig p1 up
    ifconfig p0 11.11.11.11/8 up; ip -6 a a 11:11:0:11::11/64 dev p0
    ifconfig p1 12.12.12.12/8 up; ip -6 a a 12:12:0:12::12/64 dev p1
}

stop()
{
    rmmod mlx5_ib mlx5_core
}

case "$1" in
    start|stop)
        $1
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac

