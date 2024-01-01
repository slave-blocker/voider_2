import sys 
import os 
import subprocess
from scapy.all import *
from scapy.layers.inet import IP



def chgSend(pckt):
    if IP in pckt:
        if UDP in pckt:
            print("test test  " + str(pckt[IP].src))
            if pckt[IP].src != '172.18.0.2':
                if pckt[IP].src != '0.0.0.0':
                    ###GXP patch, only same lan : 172...
                    print(pckt[IP].src)
                    print(pckt[IP].src.split('.')[0])
                    #if the call comes from a server, network namespace (10.i.1.1). :
                    if pckt[IP].src.split('.')[0][1] == '0':
                        newsrc = '172.27.' + str(pckt[IP].src.split('.')[1]) + '.1'
                    else:
                        newsrc = str(pckt[IP].src)
                    readable_payload = pckt[UDP].payload.load.decode('UTF8','replace')
                    print(newsrc + "test test  111" + readable_payload)
                    readable_payload=readable_payload.replace("172.16.3.5", newsrc)
                    print("test test  222" + readable_payload)
                    c1 = len(str(bytes(pckt[UDP].payload).decode('UTF8','replace')))
                    pckt[UDP].payload.load = bytes(readable_payload.encode('UTF8'))
                    c2 = len(str(bytes(pckt[UDP].payload).decode('UTF8','replace')))
                    c3 = c1 - c2
                    pckt[UDP].sport=5060
                    pckt[IP].len = pckt[IP].len - c3
                    pckt[UDP].len = pckt[UDP].len - c3
                    wrpcap('go', pckt)
                    if pckt[IP].src.split('.')[0][1] == '0':
                        subprocess.call(["tcprewrite", "--infile=go", "--outfile=go2f", "--enet-smac=§1", "--enet-dmac=§2", '--srcipmap=' + pckt[IP].src + ':' + newsrc, "--dstipmap=172.18.0.2:172.16.0.1", "--fixcsum"])
                    else:
                        subprocess.call(["tcprewrite", "--infile=go", "--outfile=go2f", "--enet-smac=§1", "--enet-dmac=§2", "--dstipmap=172.18.0.2:172.16.0.1", "--fixcsum"])
                    pckt2 = rdpcap('go2f')
                    sendp(pckt2, iface="§3")
while 1:
    sniff(iface="breplay", prn=chgSend)
