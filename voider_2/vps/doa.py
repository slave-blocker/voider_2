import os
import time
from pathlib import Path

os.chdir('/var/sftp/')
while True :
    for name in os.listdir('.') : 
        if os.path.isdir(name) and name != "self" :
            with open('/var/sftp/' + name + '/DoA') as file :
                doa = file.read().splitlines()
            file.close()
            try :
                if doa != '0' :
                    last_modified = int(os.path.getmtime('/var/sftp/' + name + '/DoA')) 
                    print('last_modified' + str(last_modified))
                    epoch_time = int(time.time())
                    print('epoch_time' + str(epoch_time))
                    diff = epoch_time - last_modified
                    print('diff' + str(diff))
                    if diff > 120 :
                        with open('/var/sftp/' + name + '/DoA', 'w') as file:
                            file.write('0')
                        file.close()
            except Exception :
                print("DoA_Exception")
    time.sleep(60)
