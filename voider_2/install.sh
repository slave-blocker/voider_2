#! /bin/bash

find . -name "blub" -type f -delete
curl -L https://install.pivpn.io | bash
apt install openssh-server
echo "HostKey /etc/ssh/ssh_host_ed25519_key" >> /etc/ssh/sshd_config
apt install zip
apt install bridge-utils
apt install conntrack
apt install tor
