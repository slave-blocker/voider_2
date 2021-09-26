import os
import sys
import subprocess
from shutil import copyfile

def addSftpUserToSelf():

    with open("/etc/openvpn/home_voider") as file:
        home = file.read().split()[0]
        file.close()

    if not os.path.exists("/var/sftp") :
        subprocess.run(["mkdir", "/var/sftp/"])
        subprocess.run(["chown", "root:root", "/var/sftp"])
        subprocess.run(["chmod", "755", "/var/sftp"])
        os.mkdir("/etc/ssh/voider/", 0o755 )
        file  = open("/etc/ssh/voider/backup", "w+")
        copyfile("/etc/ssh/sshd_config", "/etc/ssh/voider/backup")
        file.close()
    
    subprocess.run(["useradd", "--create-home", "self"])
    #setPassword(user_r, pass2)
    subprocess.run(["mkdir", '/var/sftp/self'])
    subprocess.run(["chown", 'root:root', '/var/sftp/self'])
    subprocess.run(["chmod", "755", '/var/sftp/self'])
    subprocess.run(["touch", '/var/sftp/self/oip'])
    subprocess.run(["chown", 'self:self', '/var/sftp/self/oip'])
    subprocess.run(["chmod", "400", '/var/sftp/self/oip'])
    
    os.mkdir('/etc/ssh/voider/self', 0o755 )
    
    List2 = [
    '\n\n\nMatch User self',
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication no",
    '\nChrootDirectory /var/sftp/self',
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no"
    ]
    
    with open('/etc/ssh/voider/self/conf', "w+") as file :
        file.writelines(List2)
    file.close()
        
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
    file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()
        
    if not os.path.exists("/etc/tor/backup") :
        copyfile("/etc/tor/torrc", "/etc/tor/backup")

    with open("/etc/tor/backup") as file :
        back = file.readlines()
    file.close()
 
    List2 = [
    '\n\n\n',
    '\nHiddenServiceDir /var/lib/tor/sshd/',
    '\nHiddenServicePort 22 127.0.0.1:22'
    ]

    back.extend(List2)
    with open("/etc/tor/torrc", 'w') as file :
        file.writelines(back)
    file.close()

    subprocess.run(["service", "tor", "restart"])

    with open("/etc/tor/torrc", 'w+') as file :
        file.writelines(back)
    file.close()

    # create the ssh key for the clients to connect over tor.
    os.mkdir(home + '/.config/voider/vps/oip_ssh', 0o755)
    copyfile("/var/lib/tor/sshd/hostname", home + '/.config/voider/vps/oip_ssh/hostname')

    os.chdir(home + '/.config/voider/vps/oip_ssh')    
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-b", "384", "-q", "-f", "self", "-N", ""])

    os.mkdir("/home/self/.ssh/", 0o755 )
    copyfile("self.pub", "/home/self/.ssh/authorized_keys")
    subprocess.run(["rm", "self.pub"])
    subprocess.run(["chmod", "640", "self"])

    subprocess.run(["service", "ssh", "restart"])


def delSftpUserToSelf():
    
    if not os.path.exists("/home/self/.ssh/authorized_keys") :
        print("Setup of self IP Address not completed.")
        sys.exit()        

    with open("/etc/openvpn/home_voider") as file:
        home = file.read().split()[0]
        file.close()
   
    # delete the ssh key for the clients to connect over tor.

    os.remove('/var/sftp/self/oip')
    os.rmdir('/var/sftp/self')
    
    os.remove(home + '/.config/voider/vps/oip_ssh/self')
    os.remove(home + '/.config/voider/vps/oip_ssh/hostname')
    os.rmdir(home + '/.config/voider/vps/oip_ssh')
    
    subprocess.run(["userdel", "-r", "self"])
        
    os.remove('/etc/ssh/voider/self/conf')
    os.rmdir('/etc/ssh/voider/self')
   
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
        file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()

    with open("/etc/tor/backup") as file :
        back = file.readlines()
    file.close()
 
    with open("/etc/tor/torrc", 'w') as file :
        file.writelines(back)
    file.close()

    subprocess.run(["service", "tor", "restart"])
    subprocess.run(["service", "ssh", "restart"])


def addSftpUser(user_rw, user_r, folder):
    
    if not os.path.exists("/home/self/.ssh/authorized_keys") :
        print("Setup of self IP Address not completed.")
        sys.exit()

    with open("/etc/openvpn/home_voider") as file:
        home = file.read().split()[0]
        file.close()    
    
    if not os.path.exists("/var/sftp") :
        subprocess.run(["mkdir", "/var/sftp/"])
        subprocess.run(["chown", "root:root", "/var/sftp"])
        subprocess.run(["chmod", "755", "/var/sftp"])
        os.mkdir("/etc/ssh/voider/", 0o755 )
        file  = open("/etc/ssh/voider/backup", "w+")
        copyfile("/etc/ssh/sshd_config", "/etc/ssh/voider/backup")
        file.close()
    
    subprocess.run(["useradd", "--create-home", user_rw])
    #setPassword(user_rw, pass1)
    subprocess.run(["useradd", "--create-home", user_r])
    #setPassword(user_r, pass2)
    subprocess.run(["usermod", "-a", "-G", user_rw, user_r])
    subprocess.run(["mkdir", '/var/sftp/' + folder])
    subprocess.run(["chown", 'root:root', '/var/sftp/' + folder])
    subprocess.run(["chmod", "755", '/var/sftp/' + folder])
    subprocess.run(["touch", '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["chmod", "750", '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["touch", '/var/sftp/' + folder + '/clients'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + folder + '/clients'])
    subprocess.run(["chmod", "750", '/var/sftp/' + folder + '/clients'])

    with open('/var/sftp/' + folder + '/DoA', 'w') as file:
        file.write('0')
    file.close()
    
    with open('/root/servers') as file:
        servers = file.readlines()
    file.close()
    
    servers.append(folder + '\n')
    
    with open("/root/servers", "w") as file:
        file.writelines(servers)
    file.close()

    os.mkdir('/etc/ssh/voider/' + user_rw, 0o755 )
    
    List2 = [
    '\n\nMatch User ' + user_rw ,
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication no",
    '\nChrootDirectory /var/sftp/' + folder,
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no\n",
    '\nMatch User ' + user_r ,
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication no",
    '\nChrootDirectory /var/sftp/' + folder,
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no"
    ]
    
    with open('/etc/ssh/voider/' + user_rw + '/conf', "w+") as file :
        file.writelines(List2)
    file.close()
    
    List2 = [
    user_rw ,
    '\n' + user_r,
    '\n' + folder
    ]
    
    with open('/etc/ssh/voider/' + user_rw + '/names', "w+") as file :
        file.writelines(List2)
    file.close()
    
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
    file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()
    
    if not os.path.exists(home + '/.config/voider/vps/new_server'):
        os.mkdir(home + '/.config/voider/vps/new_server', 0o755 )
    # create the new_server directory structure :
    os.mkdir(home + '/.config/voider/vps/new_server/DoA_ssh_write', 0o755 )
    os.mkdir(home + '/.config/voider/vps/new_server/DoA_ssh_read', 0o755 )
    os.mkdir(home + '/.config/voider/vps/new_server/oip_ssh', 0o755 )
        
    # create the ssh keys for the two new clients :
    os.mkdir('/home/' + user_rw + '/.ssh', 0o755 )
    os.chdir('/home/' + user_rw + '/.ssh/')
    #Note that the name of the user will be the same name of the ssh key file.
    #such that when the user calls it : ssh -i user user@blub.onion
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-b", "384", "-q", "-f", user_rw, "-N", ""])
    copyfile(user_rw + '.pub', '/home/' + user_rw + '/.ssh/authorized_keys')
    subprocess.run(["rm", user_rw + '.pub'])
    subprocess.run(["chmod", "640", user_rw])        
    copyfile(user_rw, home + '/.config/voider/vps/new_server/DoA_ssh_write/' + user_rw)    
    subprocess.run(["rm", user_rw ])        

    os.mkdir('/home/' + user_r + '/.ssh', 0o755 )
    os.chdir('/home/' + user_r + '/.ssh/')
    
    subprocess.run(["ssh-keygen", "-t", "ed25519", "-b", "384", "-q", "-f", user_r, "-N", ""])
    copyfile(user_r + '.pub', '/home/' + user_r + '/.ssh/authorized_keys')
    subprocess.run(["rm", user_r + '.pub'])
    subprocess.run(["chmod", "640", user_r])  
    copyfile(user_r, home + '/.config/voider/vps/new_server/DoA_ssh_read/' + user_r)
    subprocess.run(["rm", user_r ])

    # get the .onion hostname and the self key :
    copyfile(home + '/.config/voider/vps/oip_ssh/hostname', home + '/.config/voider/vps/new_server/oip_ssh/hostname')        
    copyfile(home + '/.config/voider/vps/oip_ssh/self', home + '/.config/voider/vps/new_server/oip_ssh/self')
    # put an oip file in there 
    subprocess.run(["touch", home + '/.config/voider/vps/new_server/oip_ssh/oip' ])

    # get the ports and the folder's name :
    copyfile("/root/ports", home + '/.config/voider/vps/new_server/access')
    # provide the host public key, such that the client can verify the fingerprint.    
    # such that a man-in-the-middle attack can be avoided .
    os.mkdir(home + '/.config/voider/vps/new_server/tor', 0o755 )
    os.mkdir(home + '/.config/voider/vps/new_server/direct', 0o755 )
    copyfile('/etc/ssh/ssh_host_ed25519_key.pub', home + '/.config/voider/vps/new_server/tor/host.pub')
    subprocess.run(["touch", home + '/.config/voider/vps/new_server/tor/KnownHost' ])
    copyfile('/etc/ssh/ssh_host_ed25519_key.pub', home + '/.config/voider/vps/new_server/direct/host.pub')
    subprocess.run(["touch", home + '/.config/voider/vps/new_server/direct/KnownHost' ]) 

    with open(home + '/.config/voider/vps/new_server/access') as file:
        info = file.readlines()
    file.close()      
    #only the main port is relevant for citizens    
    del info[1]
    del info[1]
    # each server is hosted at a folder, where the "DoA" and the "clients" files are.
    # the name of this folder is also used in the udp punch.
    info.append(folder + '\n')

    with open(home + '/.config/voider/vps/new_server/access', 'w') as file:
        file.writelines(info)
    file.close()

    # zip it and remove the new_server directory structure :
    
    os.chdir(home + '/.config/voider/vps/new_server/')
    subprocess.run(["zip", "-m", "-r", "self_certs.zip", "."]) 

    print("The ssh keys for the new server are available @ : " + home + '/.config/voider/vps/new_server/self_certs.zip')
    print("which also includes the port information and the name of the folder's user here.")

    subprocess.run(["service", "ssh", "restart"])

def delSftpUser(user_rw):
    
    with open('/etc/ssh/voider/' + user_rw + '/names') as file :
        L = file.read().splitlines()
    file.close()
    
    user_r = L[1]
    folder = L[2]
    
    with open("/root/servers") as file:
        Lines = file.readlines()
    file.close()
    
    Times = []
    for line in Lines :
        if not folder in line :
            Times.append(line)
    
    with open("/root/servers", "w") as file:
        file.writelines(Times)
    file.close()
    
    subprocess.run(["rm", "-r", "-f", '/var/sftp/' + folder  + '/'])    

    subprocess.run(["userdel", "-r", user_rw])
    subprocess.run(["userdel", "-r", user_r])
    subprocess.run(["groupdel", user_rw])
    
    # remove the sshd config parts respective to that user :    
    subprocess.run(["rm", "-r", "-f", '/etc/ssh/voider/' + user_rw + '/'])
    
    # load the backup file and reload the config parts 
    # respective to the remaining users.
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
    file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()
    
    subprocess.run(["service", "ssh", "restart"])

