#! /bin/bash

sleep 60s

$(cat /etc/openvpn/home_voider)/.config/voider/replay

cd /ram-dir/

python3 scaps.py &
echo "scaps.py : " $!

cd $(cat /etc/openvpn/home_voider)/.config/voider/

python3 server_deamon.py 1>server_log1 2>server_log2 &
echo "server_deamon.py : " $!
python3 clients_deamon.py 1>clients_log1 2>clients_log2 &
echo "clients_deamon.py : " $!

sleep 60s

./rp_filter_off

#python3 patch_cli.py 1>patch_log1 2>patch_log2 &
#echo "patch_cli.py : " $!

#./pid_control

#run new_gui.py manually .
FILE=/var/sftp/self/oip
if test -f "$FILE"; then
echo "$FILE exists."
cd $(cat /etc/openvpn/home_voider)/.config/voider/vps/
python3 renewIP.py 1>/dev/null 2>/dev/null &
echo "renewIP.py : " $!
python3 udp_server.py 1>/dev/null 2>/dev/null &
echo "udp_server.py : " $!
python3 doa.py 1>/dev/null 2>/dev/null &
echo "doa.py : " $!
fi
