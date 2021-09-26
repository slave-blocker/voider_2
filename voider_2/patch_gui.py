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

with open("/etc/openvpn/home_voider") as file:
    home = file.read().splitlines()[0]
file.close()

with open(home + '/.config/voider/rule') as file:
    rule = file.read()
file.close()


if( rule.split() ):
    rule = rule.replace('[','')
    rule = rule.replace(']','')
    rule = rule.replace('"','')
    rule = rule.replace(',','')
    rule = rule.replace('\'','')

    print("it's da rule " + rule)

    rule = mymodule.replace_Element(list(rule.split()), 3, "-D")

    print("it's da rule now :" + str(rule))

# something went wrong and this script needs to be rerun such that 
# the iptables rule is again fine .
# the last iptable rule is backed up in the rule file.

    subprocess.run(rule)

    with open(home + '/.config/voider/rule', 'w') as file:
        file.truncate(0)
    file.close()


