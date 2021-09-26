import os
import logging
import socket
import sys
from util import *
import threading
import random

def bind_to_random_socket(low, up):
    _counter = 0
    foo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    foo.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            _port = random.randint(low, up)
            print(_port)
            foo.bind(('', _port))
            return foo
        except Exception :
            print("port already in use")


def join(sock, pair, port, servers, addr):
    
    #print(pair)
    
    if pair[0] in servers :
        with open('/var/sftp/' + pair[0] + '/clients') as file :
            clients = file.read().splitlines()
        file.close()
        if pair[1] in clients :
            count = 0
            while count < 24 :
                data2, addr2 = sock.recvfrom(1024)
                pair2 = data2.decode("utf-8").split()
                if pair2[0] == pair[1] and pair2[1] == pair[0]:
                    print("server - send client info to: ", addr)
                    sock.sendto(addr_and_pair_to_msg(addr2, pair2), addr)
                    print("server - send client info to: ", addr2)
                    sock.sendto(addr_and_pair_to_msg(addr, pair), addr2)
                    break
                # we remain in da loop because the connection comes from 
                # the same fire starter.
                count = count + 1
        return
    if pair[1] in servers :
        with open('/var/sftp/' + pair[1] + '/clients') as file :
            clients = file.read().splitlines()
        file.close()
        if pair[0] in clients :
            count = 0
            while count < 24 :
                data2, addr2 = sock.recvfrom(1024)
                pair2 = data2.decode("utf-8").split()
                if pair2[0] == pair[1] and pair2[1] == pair[0]:
                    print("server - send client info to: ", addr)
                    sock.sendto(addr_and_pair_to_msg(addr2, pair2), addr)
                    print("server - send client info to: ", addr2)
                    sock.sendto(addr_and_pair_to_msg(addr, pair), addr2)
                    break
                count = count + 1
        return

logger = logging.getLogger()

# note that if a newuser gets registered
# then this script has to be restarted
# because this entry in the servers file needs to load.

with open("/root/servers") as file :
    servers = file.read().splitlines()
    file.close()

if not os.path.exists('/root/ports') :
    print("Please run mgmt.py .")
    exit()

with open("/root/ports") as file :
    L = file.read().splitlines()
    main_port = L[0]
    start = L[1]
    end = L[2]
    file.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', int(main_port)))

List1 = []
List2 = []
while True:
    
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print('connection from: ' + str(addr[0]) + ' @port : ' + str(addr[1]) )
    pair = data.decode("utf-8").split()
    print(pair)
    if pair[0] in servers or pair[1] in servers :
        if pair not in List1 :
            peer = [pair[1], pair[0]]
            if peer not in List1 :
                # a fresh connection from a server or a client
                # depending on wich one, he is the fire starter.
                print(start)
                print(end)
                meet = bind_to_random_socket(int(start), int(end))                
                port = meet.getsockname()[1]
                List1.append(pair)
                List2.append(port)
                with open("/var/sftp/self/oip") as file:
                    ip1 = file.read().splitlines()[0]
                    file.close()
                sock.sendto(addr_to_msg((ip1, port)), addr)
                # the fire starter will fire 24 udp probes 
                # continuosly at that meeting port.                
                threading.Thread(target=join, args=(meet, pair, port, servers, addr, )).start()            
            else :        
                # the peer wants to connect,
                # send him the meeting port
                # at wich the fire starter is looping.
                index = List1.index(peer)
                port = List2[index]
                with open("/var/sftp/self/oip") as file:
                    ip1 = file.read().splitlines()[0]
                    file.close()
                sock.sendto(addr_to_msg((ip1, port)), addr)
                # delete the entries for this meeting such
                # that it can start all again.
                del List1[index]
                del List2[index]
