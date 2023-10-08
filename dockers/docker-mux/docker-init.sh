#!/usr/bin/env bash

# Generate supervisord config file
mkdir -p /etc/supervisor/conf.d/

TZ=$(cat /etc/timezone)
rm -rf /etc/localtime
ln -sf /usr/share/zoneinfo/$TZ /etc/localtime

# The docker container should start this script as PID 1, so now that supervisord is
# properly configured, we exec supervisord so that it runs as PID 1 for the
# duration of the container's lifetime
exec /usr/local/bin/supervisord
