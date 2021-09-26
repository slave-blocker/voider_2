import os
import utils
import pwd
from pathlib import Path
from shutil import copyfile

home = str(Path.home())

print("welcome")
if not os.path.exists("/etc/openvpn/home_voider") :
    file  = open("/etc/openvpn/home_voider", "w+")
    file.write(home)
    file.close()

if not os.path.exists('/root/servers') :
    file  = open('/root/servers', "w+")
    file.close()

iSenaTor = False

print("choose option :")

print("to quit - just press enter.")
print("1 - Setup self IP Address, to be accessed over sftp over tor .")
if os.path.exists("/home/self/.ssh/authorized_keys") :
    iSenaTor = True
    print("2 - Delete self IP Address, to be accessed over sftp over tor .")
    if os.path.exists("/root/ports") :
        print("3 - Create a user. ")
        print("4 - Delete a user. ")
print("5 - Define the main port, and the port range. ")

choice = input("Enter choice integer : ")

if choice == '1' :
    
    name1 = "self"
    #pass1 = input("Enter password to read only : ")
    
    folder = "self"

    z=False
    for p in pwd.getpwall():
        if(p[0] == name1):
            z=True
            print("User already exists")

    with open("/root/servers") as file:
        Lines = file.readlines()
    file.close()
    
    for line in Lines :
        if folder in line :
            z=True
            print("Folder already exists")
            

    if not z :
        utils.addSftpUserToSelf()
        

if choice == '2' and iSenaTor :
    utils.delSftpUserToSelf()

if choice == '3' and iSenaTor :
    
    name1 = input("Enter username to read and write : ")
    #pass1 = input("Enter password to read and write : ")

    name2 = input("Enter username to read only : ")
    #pass2 = input("Enter password to read only : ")
    
    folder = input("Enter name of folder on server : ")

    z=False
    for p in pwd.getpwall():
        if(p[0] == name1):
            z=True
            print("User already exists")

    with open("/root/servers") as file:
        Lines = file.readlines()
    file.close()
    
    for line in Lines :
        if folder in line :
            z=True
            print("Folder already exists")
            

    if not z :
        utils.addSftpUser(name1, name2, folder)
    

if choice == '4' and iSenaTor :
    
    print("The following users exist :")
    L = []
    os.chdir('/etc/ssh/voider/')
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            if name != "self" :          
                print('\n' + name)
                L.append(name)
    name1 = input("Enter username to delete : ")
    
    if name1 in L:
        utils.delSftpUser(name1)
    else :
        print("Username does not exist.")

if choice == '5' :
    L=[]
    if not os.path.exists('/root/ports') :
        file = open('/root/ports', "w+")
        file.close()

    main_port = input("Enter the main port number : ")
    if int(main_port) > 1024 and int(main_port) < 65536 :
        L.append(main_port + '\n')    
    else :
        print("invalid port number")
        exit(1)

    start = input("Enter the start port number, for the port range : ")
    if int(start) > 1024 and int(start) < 65535 and int(start) != int(main_port):
        L.append(start + '\n')    
    else :
        print("invalid port number")
        exit(1)

    end = input("Enter the end port number, for the port range : ")
    if int(end) > 1025 and int(end) < 65536 and int(end) != int(main_port) and int(end) != int(start) and int(end) > int(start):
        L.append(end)    
    else :
        print("invalid port number")
        exit(1)

    with open('/root/ports', 'w') as file:
        file.writelines(L)
        file.close()

    print("Please forward ports on your router aswell, if needed.")
