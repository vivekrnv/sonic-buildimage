#!/bin/bash

# GNMI set DASH_VNET
echo "{\"Vnet1\": {\"vni\": \"45654\", \"guid\": \"559c6ce8-26ab-4193-b946-ccc6e8f930b2\"}}" > ./vnet.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_VNET:@./vnet.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get DASH_VNET
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_VNET \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI set DASH_ENI
echo "{\"F4939FEFC47E\": {\"eni_id\": \"497f23d7-f0ac-4c99-a98f-59b470e8c7bd\", \"mac_address\": \"F4939FEFC47E\", \"underlay_ip\": \"25.1.1.1\", \"admin_state\": \"enabled\", \"vnet\": \"Vnet1\"}}" > ./eni.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_ENI:@./eni.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get DASH_ENI
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_ENI \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI set DASH_ROUTING_TYPE
echo "{\"vnet\": {\"name\": \"action1\", \"action_type\": \"maprouting\"}, \"vnet_direct\": {\"name\": \"action1\", \"action_type\": \"maprouting\"}, \"vnet_encap\": {\"name\": \"action1\", \"action_type\": \"staticencap\", \"encap_type\": \"vxlan\"}}" > ./routing_type.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_ROUTING_TYPE:@./routing_type.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get DASH_ROUTING_TYPE
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_ROUTING_TYPE \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI set DASH_ROUTE_TABLE
echo "{\"F4939FEFC47E:10.1.0.0/16\": {\"action_type\": \"vnet\", \"vnet\": \"Vnet1\"}, \"F4939FEFC47E:10.1.0.0/24\": {\"action_type\": \"vnet_direct\", \"vnet\": \"Vnet1\", \"overlay_ip\": \"10.0.0.6\"}, \"F4939FEFC47E:10.2.5.0/24\": {\"action_type\": \"drop\"}}" > ./routing_type.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_ROUTE_TABLE:@./routing_type.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get DASH_ROUTE_TABLE
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_ROUTE_TABLE \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI set DASH_VNET_MAPPING_TABLE
echo "{\"Vnet1:10.0.0.6\": {\"routing_type\": \"vnet_encap\", \"underlay_ip\": \"2601:12:7a:1::1234\", \"mac_address\": \"F922839922A2\"}, \"Vnet1:10.0.0.5\": {\"routing_type\": \"vnet_encap\", \"underlay_ip\": \"100.1.2.3\", \"mac_address\": \"F922839922A2\"}, \"Vnet1:10.1.1.1\": {\"routing_type\": \"vnet_encap\", \"underlay_ip\": \"101.1.2.3\", \"mac_address\": \"F922839922A2\"}}" > ./vnet_mapping_table.txt
gnmi_set \
  -update /sonic-db:APPL_DB/DASH_VNET_MAPPING_TABLE:@./vnet_mapping_table.txt \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED

# GNMI get DASH_VNET_MAPPING_TABLE
gnmi_get \
  -xpath /sonic-db:APPL_DB/_DASH_VNET_MAPPING_TABLE \
  -cert /root/gnmiclient.cer -key /root/gnmiclient.key -ca /root/dsmsroot.cer \
  -username admin -password sonicadmin \
  -target_addr 127.0.0.1:8080 \
  -alsologtostderr \
  -xpath_target MIXED
  