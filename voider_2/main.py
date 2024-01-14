import urllib.request
import os
import sys
import re
import time
import mymodule
import socket
import subprocess
from pathlib import Path
import shutil
from shutil import copyfile

home = str(Path.home())

print("welcome")
if not os.path.exists("/etc/openvpn/home_voider") :
    file  = open("/etc/openvpn/home_voider", "w+")
    file.write(home)
    file.close()

if not os.path.exists(home + '/.config/voider/self/int_in') :
    print("Incoming interface not defined, the one connected to the phone .")
    subprocess.run(["ls", "/sys/class/net"])
    choice = input("Please type one from the above list :")
    file  = open(home + '/.config/voider/self/int_in', "w+")
    file.write(choice)
    file.close()

if not os.path.exists(home + '/.config/voider/self/int_out') :
    print("Outgoing interface not defined, the one directed to the internet .")
    subprocess.run(["ls", "/sys/class/net"])
    choice = input("Please type one from the above list :")
    file  = open(home + '/.config/voider/self/int_out', "w+")
    file.write(choice)
    file.close()
    
if not os.path.exists(home + '/.config/voider/self/phone_number') :
    phone_number = '172.16.19.84'
    gateway = '172.16.19.85' 
    L = [phone_number + '\n', gateway]
    file = open(home + '/.config/voider/self/phone_number', "w+")
    file.writelines(L)
    file.close()

if not os.path.exists(home + '/.config/voider/self/self_certs') :
    if not os.path.exists("/var/sftp/self/oip") :
        print("Do you know what port forwarding is ?")
        print("Do you want to be a vps, for citizen that don't know ?")
        print("In other words, are you a voider senator ?")
        choice = input("Please type yes or no :")
        if choice == 'yes':
            print('Please, go to : ' + home + '/.config/voider/vps/')
            print('and execute mgmt.py for that purpose.')
            sys.exit()
        if choice == 'no':
            # Not a senator :
            print("vps not defined.")
            os.mkdir( home + '/.config/voider/self/self_certs', 0o755 )
            print("place the self_certs.zip in : ")
            print(home + '/.config/voider/self/self_certs')
            os.chdir(home + '/.config/voider/self/self_certs')
            input("Press enter when done")
            subprocess.run(["unzip", "self_certs.zip"])
            subprocess.run(["chmod", "-R", "600", "."])
            subprocess.run(["rm", "self_certs.zip"])    
    
            # Assume that all virtual private servers, can run tor.
            # even if the vps has a static ip, the ip is retrieved anyway 
            # just like if it was dynamic, same difference.            
        if choice != 'no':
            if choice != 'yes':
                print("invalid input")
                sys.exit()

print("choose option :")

print("to quit - just press enter.")
print("1 - create a client connection to another server")
print("2 - delete a client connection to another server")
print("3 - call pivpn, to add a client connection to this server")
print("4 - call pivpn, to revoke a client connection to this server")
# if this server is a senator, then this option is unavailable ...
if not os.path.exists("/var/sftp/self/oip") :
    print("5 - Import access certificates, from a client")
    print("6 - Create access certificates, for a server.")
    SenaTor = False
else :
    SenaTor = True
# if this server is a senator, and we received certificates to be a client
# of a non senator, then extra code has to be written because that server 
# needs to get the DoA file from here...
# this case will not be implemented.
# A senator does not connect as a client to a non-senator . 

print(" after most executed options, a reboot is done .")

choice = input("Enter choice integer : ")

if choice == '1' :
    print('place client_certs.zip inside ' + home + '/.config/voider/servers/new_server/')
    os.chdir(home + '/.config/voider/servers/')
    index = mymodule.findfirst("occupants")
    os.chdir(home + '/.config/voider/servers/new_server/')    
    input("Press enter when done")    
    print("Please type in the servers phone number.") 
    private_phone_ip = "172.16.3.5"

    subprocess.run(["unzip", "client_certs.zip"])
    subprocess.run(["rm", "client_certs.zip"])       
    
    ovpn_cert = mymodule.getfilename(home + '/.config/voider/servers/new_server/ovpn')
    if not ovpn_cert[0]:       
        print("certificates not given (ovpn)")    
        sys.exit()
    
    oip_ssh_cert = mymodule.getfilename(home + '/.config/voider/servers/new_server/oip_ssh')
    if not oip_ssh_cert[0]:        
        print("certificates not given (oip_ssh)")    
        sys.exit()
        
    IsEnator = mymodule.IsEnatorQ(ovpn_cert[1])
    
    if not IsEnator :
        print("this connection is towards a non SenaTor.")
        DoA_ssh_read_cert = mymodule.getfilename(home + '/.config/voider/servers/new_server/DoA_ssh_read')
        if not DoA_ssh_read_cert[0]:        
            print("certificates not given (DoA_ssh_read)")    
            sys.exit()
    
    if os.path.exists(home + '/.config/voider/servers/' + str(index + 1)) :
        subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/' + str(index + 1)])
    
    mymodule.modify(home + '/.config/voider/servers/occupants', (index + 1), True, ovpn_cert[2], private_phone_ip)
    shutil.copytree(os.getcwd(), home + '/.config/voider/servers/' + str(index + 1))
    os.chdir(home + '/.config/voider/servers/' + str(index + 1))    
    subprocess.run(["chmod", "-R", "600", "."])

    # if the server is not a senator, then the folder "oip_ssh", contains the
    # ssh key for the udp_server helping with da punch.
    # if the server is a senator, then it contains the ssh key for the senator.
    # Regardless the retrieval of the ip address is the same with -> self@address.onion .                        

    subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/new_server/'])
    os.mkdir(home + '/.config/voider/servers/new_server/')

    #subprocess.run(["reboot"]) 
            

if choice == '2' :
    print("please type the index \n")
    print("i.e. x in 10.x.1.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/servers/')
    index = input("Enter index integer : ")
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            print(name)
            if(name == index):
                mymodule.modify( "occupants", int(index), False )    
                subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/' + index + '/'])
                #subprocess.run(["reboot"])


if choice == '3' :
    if not os.path.exists(home + "/.config/voider/self/new_client") :
        os.mkdir( home + "/.config/voider/self/new_client", 0o755 )                            

    name = input("Enter a Name for the Client:")
 
    private_phone_ip = "172.16.3.5"

    subprocess.run(["pivpn", "add", "-n", name, "nopass"])

    os.chdir(home + '/.config/voider/self/')
    index = mymodule.findfirst("occupants")
    List = ['ifconfig-push 172.31.0.' + str(index + 1) + ' 255.255.255.0\n',
    "push \"route 172.29.1.1 255.255.255.255 172.31.0.1\"\n",
    'iroute 172.29.' + str(index + 1) + '.1' + ' 255.255.255.255']
    os.chdir('/etc/openvpn/ccd/')
    with open(name, 'w') as file:
        file.writelines(List)
        file.close()
    
    os.chdir('/etc/openvpn/')
    if not os.path.exists("/etc/openvpn/backup") :
        file  = open("/etc/openvpn/backup", "w+")
        copyfile("/etc/openvpn/server.conf", "/etc/openvpn/backup")
        file.close()
    
    route = '\nroute 172.29.' + str(index + 1) + '.1 255.255.255.255 172.31.0.' + str(index + 1)
    mymodule.appendRoute(route)
    os.chdir(home + '/.config/voider/self/')
    mymodule.modify("occupants", (index + 1), True, name, private_phone_ip)
    if not SenaTor :    
        mymodule.addClient(name)
    
    os.chdir(home + '/ovpns/')
    with open(name + '.ovpn') as file:
        List2 = file.readlines()
        file.close()
    List3 = mymodule.changeCert(List2)

    List1 = ['#' + str(index + 1) + '\n']
    if SenaTor :
        List1.append("#1\n")
    else :
        List1.append("#0\n")
        with open(home + '/.config/voider/self/self_certs/access') as file :
            List4 = file.read().splitlines()
            file.close()
        List1.append('#' + List4[0] + '\n')
        List1.append('#' + List4[1] + '\n')
        
    with open(name + '.ovpn', '+w') as file:
        file.writelines(List1)
        file.writelines(List3)
    file.close()



    # put the openvpn certificate :
    os.mkdir(home + "/.config/voider/self/new_client/ovpn", 0o755 )    
    copyfile(home + '/ovpns/' + name + '.ovpn', home + '/.config/voider/self/new_client/ovpn/' + name + '.ovpn')    

    if not os.path.exists("/var/sftp/self/oip") :
        # this server is not a senator
        shutil.copytree(home + '/.config/voider/self/self_certs/oip_ssh/', home + '/.config/voider/self/new_client/oip_ssh/')
        
        shutil.copytree(home + '/.config/voider/self/self_certs/DoA_ssh_read/', home + '/.config/voider/self/new_client/DoA_ssh_read/')
        os.mkdir(home + '/.config/voider/self/new_client/DoA_ssh_read/DoA', 0o755 )
        subprocess.run(["touch", home + '/.config/voider/self/new_client/DoA_ssh_read/DoA/DoA'])        

        # provide the host public key, of the senator of this machine, such that the client can verify the fingerprint.    
        # such that a man-in-the-middle can be avoided .   
        shutil.copytree(home + '/.config/voider/self/self_certs/tor/', home + '/.config/voider/self/new_client/tor/')
        shutil.copytree(home + '/.config/voider/self/self_certs/direct/', home + '/.config/voider/self/new_client/direct/')
        
        #the access certificates of the senator of this client need to be known, namely @ '/.config/voider/self/clients_certs/(name_of_client)' 
        #this is done in (5) .        
    else :
        # this server is a senator
        shutil.copytree(home + '/.config/voider/vps/oip_ssh/', home + '/.config/voider/self/new_client/oip_ssh/')        
        # provide the host public key, of this machine, such that the client can verify the fingerprint.    
        # such that a man-in-the-middle attack can be avoided .   
        os.mkdir(home + '/.config/voider/self/new_client/tor', 0o755 )        
        copyfile('/etc/ssh/ssh_host_ed25519_key.pub', home + '/.config/voider/self/new_client/tor/host.pub')
        subprocess.run(["touch", home + '/.config/voider/self/new_client/tor/KnownHost' ])

    os.chdir(home + "/.config/voider/self/new_client")
    # this is given through a secured channel to the client :
    subprocess.run(["zip", "-m", "-r", "client_certs.zip", "."])
    #subprocess.run(["reboot"])

if choice == '4' :
    print("please type the index \n")
    print("i.e. x in 10.1.x.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/self/')
    index = input("Enter index integer : ")
    name = mymodule.getname( "occupants", int(index) )
    print(name)
    mymodule.modify("occupants", int(index), False ) 
    if not SenaTor :
        mymodule.delClient(name)    
        os.chdir(home + '/.config/voider/self/clients_certs')
        subprocess.run(["rm", "-r", "-f", name])    
    
    mymodule.appendRoute()
    subprocess.run(["pivpn", "revoke", "-y", name])
    #subprocess.run(["reboot"])


if not SenaTor :
    if choice == '5' :
    
        print('Place peer_certs.zip inside :' + home + '/.config/voider/self/new_peer/')
        print("The index of the client is given @ : " + home + '/.config/voider/self/new_peer/idx')
        #print(" @ : " + home + '/.config/voider/self/new_peer/idx')    
        
        os.chdir(home + '/.config/voider/self/new_peer/')
        input("Press enter when done")
    
        subprocess.run(["unzip", "peer_certs.zip"])
        subprocess.run(["rm", "peer_certs.zip"])    
        subprocess.run(["chmod", "-R", "600", "."])    
        with open("idx") as file:
            subnetID = file.read()
        file.close()
    
        with open(home + '/.config/voider/self/occupants') as file :
            clients = file.read().splitlines()
        file.close()
    
        print(clients)
        try :
            if (int(subnetID) - 2) <= len(clients) :
                client = clients[ int(subnetID) - 2 ][2:]
                if client != '' :
                    shutil.copytree(home + '/.config/voider/self/new_peer/', home + '/.config/voider/self/clients_certs/' + client + '/')
                    
                    subprocess.run(["rm", "-r", "-f", home + '/.config/voider/self/new_peer/'])
                    os.mkdir(home + '/.config/voider/self/new_peer/')                        
                    #subprocess.run(["reboot"])

        except Exception:
            print("Import error")

    if choice == '6' :
        print("The ssh certificate to access the vps over tor is @ : " + home + '/.config/voider/self/self_certs/oip_ssh')
        print("The ssh certificate to access the vps, to get the DoA file is @ : " + home + '/.config/voider/self/self_certs/DoA_ssh_read')
        print("The following certificates are available :")
        # Note : this reasoning is flawed since jonny will be jonny for all servers most likely...
        # Therefore there is no difference in the certificates names, except for the indexes...
        with open(home + '/.config/voider/servers/occupants') as file :
            certs = file.read().splitlines()
        file.close()
        
        index = 2
        for cert in certs:
            if cert[0] == '1':
                print("index : " + str(index) )
                print("10." + str(index) + ".1.1 :" + cert[2:] + "\n")
                #L.append()
            index += 1
    
        # this is the index, that matters only locally :
        choice = input("Enter certificate's index : ")
        
        # the subnetID is also an index present @ the occupants file @ the server . 
        spot = home + '/.config/voider/servers/' + str(choice) + '/ovpn/'
        with open(mymodule.getfilename(spot)[1]) as file:
            Lines = file.read().splitlines()
        file.close()

        subnetID = Lines[0][1:]
    
        os.chdir(home + '/.config/voider/self/new_peer/')

        with open("idx", '+w') as file:
            file.write(str(subnetID))
        file.close()

        L = mymodule.getfilename(home + '/.config/voider/self/self_certs/DoA_ssh_read')
        if L[0] :
            os.mkdir(home + '/.config/voider/self/new_peer/DoA_ssh_read', 0o755 )
            os.mkdir(home + '/.config/voider/self/new_peer/DoA_ssh_read/DoA', 0o755 )
            subprocess.run(["touch", home + '/.config/voider/self/new_peer/DoA_ssh_read/DoA/DoA'])
            copyfile(L[1], home + '/.config/voider/self/new_peer/DoA_ssh_read/' + L[2])

            shutil.copytree(home + '/.config/voider/self/self_certs/oip_ssh/', home + '/.config/voider/self/new_peer/oip_ssh/')
                        
            shutil.copytree(home + '/.config/voider/self/self_certs/tor', home + '/.config/voider/self/new_peer/tor')
            
            shutil.copytree(home + '/.config/voider/self/self_certs/direct', home + '/.config/voider/self/new_peer/direct')

            subprocess.run(["zip", "-m", "-r", "peer_certs.zip", "."])    
        else:
            print("certificate not given")
