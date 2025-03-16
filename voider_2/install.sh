#!/bin/sh

find . -name "blub" -type f -delete

apk add iptables sed perl git bind-tools net-tools newt curl tcpdump bridge-utils conntrack-tools bash nano

mkdir /home/$(hostname)/.config/
mv "$(pwd)/" /home/$(hostname)/.config/

cd /home/$(hostname)/.config/voider/
wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/libqrencode-tools-4.1.1-r2.apk
wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/libqrencode-4.1.1-r2.apk
apk add --allow-untrusted ./libqrencode-4.1.1-r2.apk
apk add --allow-untrusted ./libqrencode-tools-4.1.1-r2.apk
rm libqrencode-tools-4.1.1-r2.apk
rm libqrencode-4.1.1-r2.apk
wget http://dl-cdn.alpinelinux.org/alpine/v3.20/community/aarch64/tcpreplay-4.4.4-r1.apk 
apk add --allow-untrusted ./tcpreplay-4.4.4-r1.apk
rm tcpreplay-4.4.4-r1.apk

cd /home/$(hostname)/.config/voider/python/
wget https://dl-cdn.alpinelinux.org/alpine/latest-stable/community/aarch64/py3-pip-24.3.1-r0.apk
apk add --allow-untrusted ./py3-pip-24.3.1-r0.apk
rm py3-pip-24.3.1-r0.apk

python3 -m venv .
chmod +x ./bin/activate
./bin/activate
./bin/pip3 install scapy
#./bin/deactivate

cd /home/$(hostname)/.config/voider/
mv call_caller /etc/init.d/
mv call_caller.sh ../../
mv caller.sh ../../

cd /usr/local/
wget https://go.dev/dl/go1.24.0.linux-arm64.tar.gz
tar -xzf go1.24.0.linux-arm64.tar.gz

