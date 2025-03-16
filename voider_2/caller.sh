#! /bin/bash

sleep 60s

/home/$(hostname)/.config/voider/replay 1>/dev/null 2>/dev/null

cd /ram-dir/

/home/$(hostname)/.config/voider/python/bin/python3 scaps.py 1>/dev/null 2>/dev/null &
#echo "scaps.py : " $!

cd /home/$(hostname)/.config/voider/

./server_deamon 1>server_log1 2>server_log2 &
#echo "server_deamon.py : " $!
./client_deamon 1>clients_log1 2>clients_log2 &
#echo "clients_deamon.py : " $!

sleep 60s

./rp_filter_off 1>/dev/null 2>/dev/null

cd punchit

./connect_all_peers 1>peers_log1 2>peers_log2 &
