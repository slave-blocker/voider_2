import urllib.request
import os
import time
import socket
import mymodule
import subprocess
import threading
import concurrent.futures
from pathlib import Path
import util

def udp_punch(vps_ip, vps_port, server, self, num):
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 0))
    
    sock.settimeout(20)
    local_port = sock.getsockname()[1]
    address = (vps_ip, int(vps_port))
    
    print('punchit!' + str(local_port))
    e1 = threading.Event()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(mymodule.send, sock, address, self, server, e1, 3, 5)
        future = executor.submit(mymodule.receive_meeting_port, sock, e1)
        result1 = future.result()
        if result1[0] :
            sock.settimeout(120)
            address2 = result1[1]
            
            e2 = threading.Event()
    
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(mymodule.send, sock, address2, self, server, e2, 12, 10)
                future = executor.submit(mymodule.receive_client, sock, self, server, e2, num)
                result2 = future.result()
                result2.append(local_port)
                print("final")
                return result2
        else :
            return result1

def worker(num, phone):
    home = mymodule.get_home()
    print("client n° " + str(threading.get_native_id()))
    localpath = home + '/.config/voider/servers/' + str(num) 
    
    L = mymodule.getfilename(localpath + '/ovpn')
    if L[0] :    
        cert = L[2]        
        # the name of the certificate is used in the udp hole punch.
        # This way no usernames from the vps are revealed.
        # this name, is in the clients file in the server folder @ the vps of the server.            
        # this name, is unique. Because pivpn does not allow duplicate names of clients.            
        self = cert[:-5]
        full_name = L[1]        
        #print(full_name)
        with open(full_name) as file:
            Lines = file.read().splitlines()
            file.close()  
              
        subnetID = Lines[0][1:]                
        isSenator = Lines[1][1]        
        
        print(subnetID + ' ' + str(num))                
        #into the network namespace :
        subprocess.run(["ip", "route", "add", '10.' + str(num) + '.1.1', "via", '172.30.' + str(num) + '.2'])
        #into the tunnel :
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "PREROUTING", "-i", 'veth' + str(num), "-d", '10.' + str(num) + '.1.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.29.1.1"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", phone[0], "-j", "SNAT", "--to-source", '172.29.' + subnetID + '.1'])
        #out of the tunnel :
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", '172.29.' + subnetID + '.1', "-p", "all", "-j", "DNAT", "--to-destination", phone[0]])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-s", "172.29.1.1", "-j", "SNAT", "--to-source", '10.' + str(num) + '.1.1'])

        localoip_ssh_server = localpath + '/oip_ssh'

        if not isSenator == '1' :
            #----------------------------
            vps_port_server = Lines[2][1:]
            server = Lines[3][1:]
            #----------------------------
            local_DoA_ssh_read_server = localpath + '/DoA_ssh_read'
            L1 = [False, None]                  
            while True :
                print("client n° " + str(threading.get_native_id()))
                print(" Start of connection Gathering")                
                #first get the ip of the servers vps :
                #sleep here until an ip is returned.              
                while not L1[0] :            
                    L1 = mymodule.getIP(localoip_ssh_server)
                    if not L1[0] :
                        time.sleep(60)
                    else :
                        vps_ip_server = L1[1]                   
                        print('got ip address, of vps_ip_server over tor. -> ' + str(vps_ip_server))
                print(" End of connection Gathering")
                #then see if the server is online.
                #The 'DoA' file is downloaded directly, not over tor.
                #This way, the ip address for the udp punch is known.
                #sleep here until the server marks DoA = 1 . 
                #TODO : since the ip of the vps of the server is dinamic 
                # while its sleeping here the vps might change the ip ...
                # this has to be circumvented by setting a counter of failed download attempts.
                
                if  mymodule.isAlive(vps_ip_server, local_DoA_ssh_read_server) :
                    print("isAlive!")
                    result = udp_punch(vps_ip_server, vps_port_server, server, self, num)
                    print(str(result[0]))
                    if result[0] :
                        print("info received")
                        addr = result[1]
                        local_port = result[2]
                        print("local port : " + str(local_port) + ' remote host@' + addr[0] + ':' + str(addr[1]))
                 
                        subprocess.run(["iptables","-w", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])       
                        # this needs to be there because once the packets get into the default netns,
                        # they will not get masquaraded out for some unknown reason :                
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr[0], "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
                                       
                        proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num), "openvpn", "--lport", str(local_port), "--remote", str(addr[0]), str(addr[1]), "--config", full_name, "--float"])
                        time.sleep(20)
                        count = 0
                        connected = True
                        while connected :
                            print('Worker' + str(num))
                            if mymodule.ping("172.31.0.1", num) :
                                print("ping succeeded")
                                count = 0
                                time.sleep(15)
                            else :
                                if count == 5 :
                                    proc.terminate()
                                    connected = False
                                    # dinamic ip might have changed therefore need to delete iptable rules :
                                    subprocess.run(["iptables","-w", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
                                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-D", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr[0], "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
                                else :
                                    print('ping ' + str(count) + ' failed')
                                    time.sleep(5)
                                    count = count + 1
                else :
                    print("3 sftp download attempts failed")
                    L1 = [False, None]
        else :
            L2 = [False, None]
            while True :
                while not L2[0] :            
                    L2 = mymodule.getIP(localoip_ssh_server)
                    if not L2[0] :
                        time.sleep(60)
                    else :
                        addr = L2[1]                   
                        print('got ip address, of vps_ip_server over tor. -> ' + str(addr))
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', 0))
                local_port = sock.getsockname()[1]                        
                                                
                subprocess.run(["iptables","-w", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
                # this needs to be there because once the packets get into the default netns,
                # they will not get masquaraded out for some unknown reason :                
                subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr, "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
                proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num), "openvpn", "--lport", str(local_port), "--remote", str(addr), "--rport", "1194", "--config", full_name])
                time.sleep(1)
                subprocess.run(["conntrack", "-D", "-p", "UDP", "-s", addr])
                subprocess.run(["conntrack", "-D", "-p", "UDP", "-d", addr])
                subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-s", addr])
                subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-d", addr])
                time.sleep(20)
                count = 0
                connected = True
                while connected :
                    print('Worker' + str(num))
                    if mymodule.ping("172.31.0.1", num) :
                        print("ping succeeded")
                        count = 0
                        time.sleep(15)
                    else :
                        if count == 5 :
                            proc.terminate()
                            connected = False
                            L2 = [False, None]                        
                            # dinamic ip might have changed therefore need to delete iptable rules :
                            subprocess.run(["iptables","-w", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
                            subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables","-w", "-t", "nat", "-D", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr, "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
                        else :
                            print('ping ' + str(count) + ' failed')
                            time.sleep(5)
                            count = count + 1        
    else :
        print("no openvpn certificate present")    
    
    return

home = mymodule.get_home()

#subprocess.run(["iptables","-w", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self' ), "-j", "MASQUERADE"])

subprocess.run(["iptables","-w", "-t", "nat", "--flush"])
subprocess.run(["iptables", "-t", "filter", "--flush"])

with open(home + '/.config/voider/self/phone_number') as file:
    phone = file.read().splitlines()
file.close()

os.chdir(home + '/.config/voider/servers')

with open("occupants") as file:
    Lines = file.read().splitlines()
file.close()

print(Lines) 



netns = 2
for line in Lines :
    if line[0] == '1' :
        print(line)
        subprocess.run(["ip", "netns", "add", 'netns' + str(netns)])
        subprocess.run(["brctl", "addbr", 'br' + str(netns)])
        subprocess.run(["ip", "addr", 'add', '172.30.' + str(netns) + '.1/24', "dev", 'br' + str(netns)])
        subprocess.run(["ip", "link", "set", "dev", 'br' + str(netns), "up"])
        subprocess.run(["ip", "link", "add", 'veth' + str(netns), "type", "veth", "peer", "name", 'veth-br'  + str(netns)])
        subprocess.run(["ip", "link", "set", 'veth' + str(netns), "netns", 'netns' + str(netns)])
        subprocess.run(["brctl", "addif", 'br' + str(netns), 'veth-br'  + str(netns)])
        subprocess.run(["ip", "link", "set", "dev", 'veth-br'  + str(netns), "up"])
        netns = netns + 1

print("line")

netns = 2
for line in Lines :
    if line[0] == '1' :
        print(line)
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"iptables","-w", "-t", "nat", "--flush"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"iptables", "-t", "filter", "--flush"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "addr", "add", '172.30.' + str(netns) + '.2/24', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", "lo", "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", 'veth' + str(netns), "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "route", "add", "default", "via", '172.30.' + str(netns) + '.1', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "iptables", "-A", "OUTPUT", "-o", 'veth' + str(netns), "-d", "172.31.0.1", "-j", "DROP"])
        netns = netns + 1


# spawn n processes, one for each ovpn client

print("main " + str(os.getpid()))

with open(home + '/.config/voider/client_pid', 'w') as file:
    file.write(str(os.getpid()))
file.close()

N=[]
T=[]

netns = 2
for line in Lines :
    if line[0] == '1' :
        t = threading.Thread(target=worker, args=(netns, phone, ))
        t.daemon = True
        N.append(netns)
        T.append(t)
    netns = netns + 1

time.sleep(10)

while True :
    c=0
    for thread in T :
        if not thread.is_alive() :
            T[c] = threading.Thread(target=worker, args=(N[c], phone, ))            
            T[c].daemon = True
            T[c].start()
        else :
            print('thread ' + str(c) + ' is_alive')
            print(str(thread.is_alive()))
            print("indeed")
        c+=1
    time.sleep(30)
