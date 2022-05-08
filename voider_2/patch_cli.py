import urllib.request
import os
import time
import socket
import subprocess
import mymodule
import re
from pathlib import Path
import threading
import concurrent.futures

subprocess.run(["killall", "tcpdump"])

with open("/etc/openvpn/home_voider") as file:
    home = file.read().splitlines()[0]
file.close()

localpath = home + '/.config/voider/self/'

with open(localpath + 'occupants') as file:
    clients = file.read().splitlines()
file.close()

m1 = []
m2 = []

x=1

for client in clients :
    if client[0] == '1':
        callee1 = '10.1.'+ str(x + 1) +'.1'
        callee2 = '172.29.'+ str(x + 1) + '.1'
        m1.append(callee1)
        m2.append(callee2)
    x += 1

mymodule.patch_caller(m1, m2)
