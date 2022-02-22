#! /bin/bash

sleep 60s

cd /home/§/.config/voider/

./rp_filter_off

python3 server_deamon.py 1>/dev/null 2>/dev/null &
echo "server_deamon.py : " $!
python3 clients_deamon.py 1>/dev/null 2>/dev/null &
echo "clients_deamon.py : " $!
python3 patch_cli.py 1>/dev/null 2>/dev/null &
echo "patch_cli.py : " $!

#run new_gui.py manually .
FILE=/var/sftp/self/oip
if test -f "$FILE"; then
echo "$FILE exists."
cd vps
python3 renewIP.py 1>/dev/null 2>/dev/null &
echo "renewIP.py : " $!
python3 udp_server.py 1>/dev/null 2>/dev/null &
echo "udp_server.py : " $!
python3 doa.py 1>/dev/null 2>/dev/null &
echo "doa.py : " $!
fi
