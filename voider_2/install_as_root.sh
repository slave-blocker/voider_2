#!/bin/bash

echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile

echo net.ipv6.conf.all.disable_ipv6=1 >> /etc/sysctl.conf
echo net.ipv6.conf.default.disable_ipv6=1 >> /etc/sysctl.conf
echo net.ipv6.conf.lo.disable_ipv6=1 >> /etc/sysctl.conf

sysctl -p

curl -L https://install.pivpn.io | bash
sed -i "20 s/.*/pivpnNET=172.31.0.0/" /etc/pivpn/wireguard/setupVars.conf
sed -i "22 s/.*/pivpnenableipv6=0/" /etc/pivpn/wireguard/setupVars.conf
sed -i "3 s?.*?Address = 172.31.0.1/24?" /etc/wireguard/wg0.conf

wget https://dl-cdn.alpinelinux.org/alpine/v3.20/community/aarch64/tor-0.4.8.14-r0.apk
apk add --allow-untrusted ./tor-0.4.8.14-r0.apk
wget https://gitlab.alpinelinux.org/alpine/aports/-/raw/master/community/tor/tor.initd
mv tor.initd /etc/init.d/tor
chmod +x /etc/init.d/tor
mv /etc/tor/torrc.sample /etc/tor/torrc

rc-update add tor default
/etc/init.d/tor start

rc-update add call_caller default
/etc/init.d/call_caller start

reboot
