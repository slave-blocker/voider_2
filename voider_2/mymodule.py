import socket
import os
import subprocess
import re
import time
import util
import random
from pathlib import Path
import fcntl
import struct
import select
import threading
import sys
import ipaddress

def get_home():
    with open("/etc/openvpn/home_voider") as file:
        home = file.read().splitlines()[0]
        file.close()
    return home

def replace_Element(L, index, el):
    temp=[]
    i = 0
    for element in L :
        if( index == i ):
            temp.append(el)
        else :
            temp.append(L[i])
        i+=1
    return temp

def getint_in():
    home = get_home()    
    localpath = home + '/.config/voider/self/' 
    with open(localpath + 'int_in') as file:
        int_eth = file.read()
    file.close()
    return int_eth

def getint_out():
    home = get_home()    
    localpath = home + '/.config/voider/self/' 
    with open(localpath + 'int_out') as file:
        int_wlan = file.read()
    file.close()
    return int_wlan

def getname(occupants, index):
    with open(occupants) as file:
        Lines = file.readlines()
        name = Lines[index - 2].split('#')[1].strip();
    file.close()
    return name

def get_phone():
    home = get_home()    
    with open(home + '/.config/voider/self/phone_number') as file:
        phone = file.read().splitlines()[0]
    file.close()
    return phone

# gets the name of the first file inside the directory
# in this context, directories of interest only have one file.
def getfilename(path):
    for name in os.listdir(path) :
        #print(path + '/' + cert) 
        if os.path.isfile(path + '/' + name) :
            full_name = path + '/' + name
            return [True, full_name, name]       
    return [False, None, None]

def findfirst(occupants):
    with open(occupants) as file:
        Lines = file.readlines() 
# Strips the newline character 
    file.close()
    count = 1
    for line in Lines:
        if(line.strip()[0] == '0'):
            return count 
        count = count + 1
    return count

def IsEnatorQ(path):
    with open(path) as file:
        Lines = file.read().splitlines()
        file.close()
    if Lines[1][1] == "1" :
        return True
    else :
        return False

def modify(occupants, index, do, name = None, phone):
    with open(occupants) as file:
        Lines = file.readlines() 
    file.close()
    print(Lines)
    if len(Lines) == 0 :
        Lines.append('1#' + name + "#" + phone)
    else :
        if ( index - 2 ) <= (len(Lines) - 1)  : 
            if ( index - 2 ) == (len(Lines) - 1) :
                if do :
                    Lines[index - 2] = str(1) + '#' + name + "#" + phone
                if not do :
                    Lines[index - 2] = str(0)
            else :
                if do :
                    Lines[index - 2] = str(1) + '#' + name  + "#" + phone + '\n'
    
                if not do :
                    Lines[index - 2] = str(0) + '\n'
        else :
            Lines.append('\n1#' + name + "#" + phone)
        
    with open(occupants, 'w') as file:
        file.writelines(Lines)
    file.close()
    return
    
def appendRoute(route = None):
    home = get_home()    
    with open(home + '/.config/voider/self/occupants') as file:
        Lines = file.readlines() 
    file.close()
    List = []
    j = 2
    for line in Lines :
        if line[0] == '1' :
            List.append('\nroute 172.29.' + str(j) + '.1' + ' 255.255.255.255 172.31.0.' + str(j))
        j = j + 1
    
    with open('/etc/openvpn/backup') as file:
        Lines = file.readlines()
    file.close()
    for routes in List :
        Lines.append(routes)
    if route != None : 
        Lines.append(route)
    
    Times = []
    for line in Lines :
        z = False
        z2 = False

        if "dhcp-option" in line :
            z = True
        if "block-outside-dns" in line :
            z = True
        if "redirect-gateway" in line :
            z = True
        if "server 10.8" in line :
            z2 = True
        
        if z :
            Times.append('#' + line)
        else :
            if z2 :
                Times.append("server 172.31.0.0 255.255.255.0\n")
            else :
                Times.append(line)
    
    
    with open('/etc/openvpn/server.conf', 'w') as file:
        file.writelines(Times)
    file.close()
    return

def changeCert(Lines):
   
    Times = []
    for line in Lines :
        z = False

        if "nobind" in line :
            z = True
       
        if z :
            Times.append('#' + line)
        else :
            Times.append(line)
    return Times
    
def addClient(name):
    home = get_home()

    localoip_ssh = home + '/.config/voider/self/self_certs/oip_ssh'

    host = getIP(localoip_ssh)[1]
  
    localpath = home + '/.config/voider/self/clients'
    
    with open(localpath) as file:
        L = file.readlines()
    file.close()
    
    L.append(name + '\n')
    
    with open(localpath, "w") as file:
        file.writelines(L)
    file.close()
    
    remotepath = '/clients'
    
    Upload(localpath, remotepath, host)
    
def delClient(name):
    home = get_home()

    localoip_ssh = home + '/.config/voider/self/self_certs/oip_ssh/'

    host = getIP(localoip_ssh)[1]

    localpath = home + '/.config/voider/self/clients'
    
    with open(localpath) as file:
        Lines = file.readlines()
    file.close()
    
    Times = []
    for line in Lines :
        if not name in line :
            Times.append(line)
    
    with open(localpath, "w") as file:
        file.writelines(Times)
    file.close()

    remotepath = '/clients'
    
    Upload(localpath, remotepath, host)

#this method serves for Uploading The DoA file and the clients file, to the vps of the server.
def Upload(localpath, remotepath, host):
    home = get_home()
    sftp = home + '/.config/voider/sftp'
    [gotit, key, name] = getfilename(home + '/.config/voider/self/self_certs/DoA_ssh_write')
    cwd = home + '/.config/voider/self/self_certs/direct'
    if gotit :    
        proc = subprocess.Popen([sftp, key, name, host, remotepath, localpath, "direct", "put", cwd])
        print("after subprocess.Popen @Upload")
        try :
            proc.wait(10)
        except subprocess.TimeoutExpired:
            print("Upload sftp TimeoutExpired")
            proc.terminate()
            return False
        except Exception:
            print("Upload sftp failed")
            proc.terminate()
            return False
        return True
    else :
        print("no certificate present")
        sys.exit()
    
#this method serves for Downloading The DoA file only, from the vps of the server.
def Download(localpath, host, local_DoA):
    home = get_home()    
    sftp = home + '/.config/voider/sftp'
    [gotit, full_name, name] = getfilename(localpath)
    cwd = localpath + '/../direct'
    if gotit :    
        proc = subprocess.Popen([sftp, full_name, name, host, "/DoA", local_DoA, "direct", "get", cwd])
        print("after subprocess.Popen @Download")
        try :
            proc.wait(10)
        except subprocess.TimeoutExpired:
            print("Download sftp TimeoutExpired")
            proc.terminate()
            return False
        except Exception:
            print("Download sftp failed")
            proc.terminate()
            return False
        return True
    else :
        print("no certificate present")
        sys.exit()

def Download_onions_IP(localoip_ssh, onion):
    if os.path.exists(localoip_ssh + "/self") :    
        #TODO counter check the ssh host hash, to prevent a man-in-the-middle attack
        home = get_home()    
        sftp = home + '/.config/voider/sftp'
        #print("1 " + sftp)
        key = localoip_ssh + "/self"
        localoip = localoip_ssh + "/oip"
        #print("2 " + key)
        #print("4 " + onion)
        #print("6 " + localoip)
        cwd = localoip_ssh + '/../tor'       
        proc = subprocess.Popen([sftp, key, "self", onion, "/oip", localoip, "tor", "get", cwd])
        print("after subprocess.Popen @Download_onions_IP")        
        try :
            proc.wait(30)
        except subprocess.TimeoutExpired:
            print("Download_onions_IP sftp TimeoutExpired")
            proc.terminate()
            return False
        except Exception:
            print("Download_onions_IP sftp failed")
            proc.terminate()
            return False
        return True
    else :
        print("no certificate present")
        sys.exit()

def isAlive(vps_ip, localpath):        
    isDead = True
    local_DoA = localpath + '/DoA/DoA'
    fail = 0
    while isDead:
        
        if Download(localpath, vps_ip, local_DoA):
            with open(local_DoA) as file:
                DoA = file.read().splitlines()
                file.close()
            try :            
                if DoA[0] == '1':
                    isDead = False
                else:
                    if DoA[0] == '0':
                        fail = 0
                        time.sleep(60)
            except Exception :
                print("error @ Download_onions_IP ")
        else:
            if fail == 3 :                
                return False                    
            else :                
                fail += 1
                
    return True

def isIPv4_addr(ip_addr) :
    try:
        ip = ipaddress.ip_address(ip_addr)
        return True    
    except Exception :
        return False

def getIP(localoip_ssh) :
    isDead = True
    oip = 0

    with open(localoip_ssh + '/hostname') as file:
        onion = file.read().splitlines()[0]
        file.close()

    localoip = localoip_ssh + '/oip'    
    fail = 0
    while isDead:
        
        if Download_onions_IP(localoip_ssh, onion) :
            print("after Download_onions_IP")
            with open(localoip) as file:
                DoA = file.read().splitlines()
                file.close()
            try :
                print("after try")
                print("0 this is AoD : " + DoA[0])
                if isIPv4_addr(DoA[0]) :#if no ip was downloaded, within 10 secs, the file just contains a 0.
                    print("Ip is valid : " + DoA[0])
                    isDead = False
                    oip = DoA[0]
                else:
                    print("Ip is invalid : " + DoA[0])
                    time.sleep(60)
            except Exception :
                print("error @ Download_onions_IP ")
                time.sleep(60)
        else:
            if fail == 3 :                
                return [False, None]                    
            else :                
                fail += 1
    return [True, oip]

def send(sock, addr, self, peer, event, limit, sleep):
    message = self + ' ' + peer
    message = str.encode(message)
    count = 0
    while count < limit and not event.is_set():
        print('gogogo ' + str(count) + self + ' ' + peer + ' ' + str(addr[1]))
        sock.sendto(message, addr)
        time.sleep(random.randint(1, sleep))
        count = count + 1
        
def receive_meeting_port(sock, event):
    try:
        data, addr = sock.recvfrom(1024)
        event.set()
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(5)
        result = [False, None]
        return result
        
    print('peer received from vps : {} {}'.format(addr, data))
    addr = util.msg_to_addr(data)
    
    #sock.close()
    result = [True, addr]
        
    return result


def receive_server(sock, self, peer, event):
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(10)
        result = [False, None]
        return result
    
    print('peer received from vps : {} {}'.format(addr, data))
    temp = util.msg_to_addr_and_pair(data)
    addr = (temp[0], temp[1])
    pair = [temp[2], temp[3]]

#    print(pair[0] + ' ' + pair[1])
#    print("punch")
#    print(peer + ' ' + self)


    if pair[0] == peer and pair[1] == self:
        event.set()
        print("punch the hole through !")
        message = self + ' ' + peer
        message = str.encode(message)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("punch done, now rest...")

        print("activate the client's nat rule .")
        time.sleep(10)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("just sent 6 packets")        
        
        sock.close()
    
        result = [True, addr]
        
        return result
    else:
        result = [False, addr]
        
        return result    
    
def receive_client(sock, self, peer, event, num):
    home = get_home()
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(10)
        result = [False, None]
        return result
        
    print('peer received from vps : {} {}'.format(addr, data))
    temp = util.msg_to_addr_and_pair(data)
    addr = (temp[0], temp[1])
    pair = [temp[2], temp[3]]

    #print(pair[0] + ' ' + pair[1])
    #print("punch")
    #print(peer + ' ' + self)


    if pair[0] == peer and pair[1] == self:
        event.set()
        print("punch the hole through !")
        message = self + ' ' + peer
        message = str.encode(message)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("punch done, now rest...")
        time.sleep(5)
        
        subprocess.run(["iptables", "-w", "-t", "nat", "-A", "PREROUTING", "-i", getint_out(), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr[0], "-j", "SNAT", "--to-source", get_ip_address(getint_out())])
        subprocess.run(["conntrack", "-D", "-p", "UDP", "-s", addr[0]])
        subprocess.run(["conntrack", "-D", "-p", "UDP", "-d", addr[0]])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-s", addr[0]])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-d", addr[0]])

        print("expecting incoming packets to activate own nat rule.")
        time.sleep(10)
        
        sock.close()
    
        result = [True, addr]
        
        return result
    else:
        result = [False, addr]
        
        return result    

def ping(host, netns):
    try:
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ping", "-c", "1", "-W", "3", host], check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
        
def ping2(host):
    try:
        subprocess.run(["ping", "-c", "1", "-W", "3", host], check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', (ifname[:15].encode('utf-8')))
    )[20:24])
