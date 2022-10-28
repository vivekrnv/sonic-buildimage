#!/bin/bash

# Create Root key and cert
openssl genrsa -out dsmsroot.key 2048
openssl req -new -sha256 -out dsmsroot.csr -key dsmsroot.key -config dsmsroot.conf -batch
openssl x509 -req -days 3650 -in dsmsroot.csr -signkey dsmsroot.key -out dsmsroot.cer

# Create server key and cert
openssl genrsa -out gnmiserver.key 2048
openssl req -new -sha256 -out gnmiserver.csr -key gnmiserver.key -config server.conf -batch
openssl x509 -req -days 3650 -CA dsmsroot.cer -CAkey dsmsroot.key -CAcreateserial -in gnmiserver.csr -out gnmiserver.cer -extensions req_ext -extfile server.conf

# Create client key and cert
openssl genrsa -out gnmiclient.key 2048
openssl req -new -sha256 -out gnmiclient.csr -key gnmiclient.key -config client.conf -batch
openssl x509 -req -days 3650 -CA dsmsroot.cer -CAkey dsmsroot.key -CAcreateserial -in gnmiclient.csr -out gnmiclient.cer -extensions req_ext -extfile client.conf
