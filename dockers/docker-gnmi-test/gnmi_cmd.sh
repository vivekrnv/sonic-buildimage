#!/bin/bash

# GNMI capabilities
gnmi_cli -client_types=gnmi -a 127.0.0.1:8080 -logtostderr -capabilities -client_crt /root/gnmiclient.cer -client_key /root/gnmiclient.key -ca_crt /root/dsmsroot.cer

# GNMI set update
echo "{\"qos_01\": {\"bw\": \"54321\", \"cps\": \"1000\", \"flows\": \"300\"}}" > ./update.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_QOS:@./update.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_QOS \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI set delete
gnmi_set \
  -delete /sonic-db:APPL_DB/DASH_QOS/qos_01 \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_QOS \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED