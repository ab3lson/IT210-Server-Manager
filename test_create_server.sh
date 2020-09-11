#! /bin/bash

pct create $(pvesh get /cluster/nextid) \
    /var/lib/vz/template/cache/ubuntu-20.04-standard_20.04-1_amd64.tar.gz \
    --cores 2 --cpuunits 2048 \
    --memory 4096 --swap 512 \
    --hostname student001Server \
    --net0 name=eth0,ip=192.168.10.60/24,bridge=vmbr0,gw=192.168.4.1 \
    --rootfs local-lvm:16 \
    --onboot 1