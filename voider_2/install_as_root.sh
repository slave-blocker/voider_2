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

rc-update add call_caller default
/etc/init.d/call_caller start

reboot
