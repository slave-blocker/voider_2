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


def udp_punch(client, localpath, idx):
    home = mymodule.get_home()

    localoip_ssh_client = localpath + '/oip_ssh'
    
    with open(home + '/.config/voider/self/self_certs/access') as file:
        access = file.read().splitlines()
        file.close()
    
    # this is a multi-cloud system.
    # the server checks the DoA file of the client at the clients vps
    # the client checks the DoA file of the server at the servers vps
    # the client always connects to the server,
    # over the vps of the server. 
    
    local_DoA_ssh_read_client = localpath + '/DoA_ssh_read'

    #----------------------------------                
    localoip_ssh_server = home + '/.config/voider/self/self_certs/oip_ssh'
    vps_port_server = access[0]    
    folder = access[1]
    #----------------------------------
    L1 = [False, None]
    while True :
        print(" Start of connection Gathering")
        
        while not L1[0] :            
            L1 = mymodule.getIP(localoip_ssh_client)
            if not L1[0] :                                     
                time.sleep(60)
            else :
                vps_ip_client = L1[1]                   
                print(str(idx) + '<---IDX;;;got ip address, of vps_ip_client over tor. -> ' + str(vps_ip_client))

        L2 = [False, None]      
        while not L2[0] :            
            L2 = mymodule.getIP(localoip_ssh_server)
            if not L2[0] :                                     
                time.sleep(60)
            else :
                vps_ip_server = L2[1]                   
                print(str(idx) + '<---IDX;;;got ip address, of vps_ip_server over tor. -> ' + str(vps_ip_server))            

        print(" End of connection Gathering")

        if mymodule.isAlive(vps_ip_client, local_DoA_ssh_read_client):
            print("isAlive")
            #note that this might lead to synchronization issues,
            #because downloading a file over sftp over tor might lead to lags !
            #here vps_ip_server means vps_ip_{me me ME}               
            address = (vps_ip_server, int(vps_port_server))
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 0))
            local_port = sock.getsockname()[1]
            sock.settimeout(20)
            e1 = threading.Event()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(mymodule.send, sock, address, folder, client, e1, 3, 5)
                future = executor.submit(mymodule.receive_meeting_port, sock, e1)
                result1 = future.result()
                if result1[0] :
                    sock.settimeout(120)
                    address2 = result1[1]
                    e2 = threading.Event()
                   
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(mymodule.send, sock, address2, folder, client, e2, 12, 10)
                        future = executor.submit(mymodule.receive_server, sock, folder, client, e2)
                        result2 = future.result()
                
                        if result2[0] :
                            print("info received")
                            addr = result2[1]
                            print(str(local_port))
                            subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out(), "-p", "UDP", "--dport", str(local_port), "-j", "REDIRECT", "--to-port", "1194"])
                            subprocess.run(["conntrack", "-D", "-p", "UDP"])
                            print("nat REDIRECT rule set")
                            time.sleep(25)
                
                            count = 0
                            connected = True
                            while connected :
                                if mymodule.ping2('172.31.0.' + str(idx)) :
                                    print("ping succeeded")
                                    count = 0
                                    time.sleep(15)
                                else :
                                    if count == 5 :
                                        connected = False
                                        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out(), "-p", "UDP", "--dport", str(local_port), "-j", "REDIRECT", "--to-port", "1194"])
                                    else :
                                        print('ping ' + str(count) + ' failed')
                                        time.sleep(5)
                                        count = count + 1
        else :
            print("3 sftp download attempts failed")    
            L1 = [False, None]

def connect_to_clients():
    home = mymodule.get_home()
    localpath = home + '/.config/voider/self'
    
    with open(localpath + '/occupants') as file:
        clients = file.read().splitlines()
    file.close()

    idx = 1
    for client in clients :
        idx = idx + 1
        if client[0] == '1':
            splitted_string = client.split("#")    
            name = splitted_string[1]
            temp = localpath + '/clients_certs/' + name
            threading.Thread(target=udp_punch, args=(name, temp, idx, )).start()

home = mymodule.get_home()

with open(home + '/.config/voider/self/phone_number') as file:
    phone = file.read().splitlines()
file.close()

# place the needed nat rules 

subprocess.run(["iptables", "-t", "nat", "--flush"])
subprocess.run(["ip", "addr", "add", phone[1] + '/29', "dev", mymodule.getint_in()])

subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out(), "-j", "MASQUERADE"])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "brsip", "-s", phone[0], "-j", "SNAT", "--to-source", "172.18.0.2"])


# into the tunnel :
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", phone[0], "-p", "udp", "!", "--dport", "5060", "-j", "SNAT", "--to-source", "172.29.1.1"])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.18.0.2", "-p", "udp", "--dport", "5060", "-j", "SNAT", "--to-source", "172.29.1.1"])


# out of the tunnel :
#subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "all", "-j", "DNAT", "--to-destination", phone[0]])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "udp", "!", "--dport", "5060", "-j", "DNAT", "--to-destination", phone[0]])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "udp", "--dport", "5060", "-j", "DNAT", "--to-destination", "172.18.0.2"])


localpath = home + '/.config/voider/self'

with open(localpath + '/occupants') as file:
    clients = file.read().splitlines()
file.close()

x=1

for client in clients :
    splitted_string = client.split("#")    
    if splitted_string[0][0] == '1' :    
        callee1 = '10.1.'+ str(x + 1) +'.1'
        callee2 = '172.29.'+ str(x + 1) + '.1'
    # nat into the bridge to fool conntrack :
    # 7000 + client idx 
        portroute = 7000 + (x + 1)
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-I", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", phone[0], "-d", '10.1.' + str(x + 1) + '.1', "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute)])
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", phone[0], "-d", '172.29.' + str(x + 1) + '.1', "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute), "-m", "comment", "--comment", "Ack and Bye like rtp"])
        subprocess.run(["ip", "netns", "exec", "replay", "ip", "route", "add", '172.29.' + str(x + 1) + '.1', "via", "172.18.0.1"])
        subprocess.run(["ip", "netns", "exec", "replay", "iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "vethsip", "-d", "172.19.0.2", "-p", "udp", "--dport", str(portroute), "-j", "DNAT", "--to-destination", '172.29.' + str(x + 1) + '.1:5060'])
    x += 1



# if this machine is not a Senator :
if not os.path.exists("/var/sftp/self/oip") :
    threading.Thread(target=connect_to_clients, args=()).start()

    localoip_ssh = home + '/.config/voider/self/self_certs/oip_ssh'
    localpath = home + '/.config/voider/self/DoA'
    remotepath = '/DoA'

    L3 = [False, None]
    while(True):
        print("uploading")
        while not L3[0] :            
            L3 = mymodule.getIP(localoip_ssh)
            if not L3[0] :                                     
                time.sleep(60)
            else :
                vps_ip_server = L3[1]                   
                print('got ip address, of vps_ip_server over tor. -> ' + str(vps_ip_server))            
    
        while mymodule.Upload(localpath, remotepath, vps_ip_server) :
            print("after Upload")
            time.sleep(60)

# if this machine is a Senator then clients connect to it directly without udp holepunch
