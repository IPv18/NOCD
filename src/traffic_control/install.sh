#!/bin/bash

# install traffic control linux requirements
#   - enable cgroup v2
#   - enable net_cls cgroup



# Check if cgroup v2 is already enabled
if grep -q cgroup2 /proc/filesystems; then
    echo "cgroup v2 is already enabled"
else
    # Mount cgroup v2
    mkdir /sys/fs/cgroup/unified
    mount -t cgroup2 none /sys/fs/cgroup/unified
    
    # Enable cgroup v2 at boot
    echo "none /sys/fs/cgroup/unified cgroup2 0 0" >> /etc/fstab
    
    # Reboot to apply changes
    echo "cgroup v2 has been enabled, rebooting now..."
    #reboot
fi

# Check if net_cls cgroup is already enabled
if grep -q net_cls /proc/cgroups; then
    echo "net_cls cgroup is already enabled"
else
    # Enable net_cls cgroup
    mkdir /sys/fs/cgroup/net_cls
    sudo mount -t cgroup -o net_cls net_cls /sys/fs/cgroup/net_cls

    # Reboot to apply changes
    echo "net_cls cgroup has been enabled, rebooting now..."
    #reboot
fi