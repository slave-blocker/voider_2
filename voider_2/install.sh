#! /bin/bash

find . -name "blub" -type f -delete

sed -i 's/§/'"$(whoami)"'/g' rc.local
sed -i 's/§/'"$(whoami)"'/g' caller.sh

sudo mv rc.local /etc/

cd ..
mkdir ~/.config
mv voider_2 ~/.config/voider

sudo apt-get install tcpdump conntrack bridge-utils tor zip openssh-server
curl -L https://install.pivpn.io | bash

echo "HostKey /etc/ssh/ssh_host_ed25519_key" >> /etc/ssh/sshd_config
