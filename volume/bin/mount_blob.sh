#!/bin/bash

mkdir -p /root/etc/blob
cp /root/volume/etc/blob/blob-passwd /root/etc/blob/blob-passwd
chmod 600 /root/etc/blob/blob-passwd

mkdir -p /root/mnt/blob
blobfuse /root/mnt/blob --tmp-path=/mnt/blobfusetmp -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 --config-file=/root/etc/blob/blob-passwd
