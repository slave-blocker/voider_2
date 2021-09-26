from tkinter import *
from PIL import Image, ImageTk
import subprocess
import time
import mymodule
import threading
import copy

def close_window():
    subprocess.Popen(["killall", "tcpdump"])
    raise SystemExit

def boot_patch(home, m1, m2, call_started):
    subprocess.Popen(["killall", "tcpdump"])
    proc = subprocess.Popen(["python3", "patch_gui.py"])
    threading.Thread(target=mymodule.patch, args=(home, m1, m2, call_started, )).start()

with open("/etc/openvpn/home_voider") as file:
    home = file.read().splitlines()[0]
file.close()

localpath = home + '/.config/voider/self/'

with open(localpath + 'occupants') as file:
    clients = file.read().splitlines()
file.close()

m1 = []
m2 = []

x=1

for client in clients :
    if client[0] == '1':
        callee1 = '10.1.'+ str(x + 1) +'.1'
        callee2 = '172.29.'+ str(x + 1) + '.1'
        m1.append(callee1)
        m2.append(callee2)
    x += 1

call_started = threading.Event()

boot_patch(home, m1, m2, call_started)

class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.label1 = Label(text="servers :         gateways :           using gateway :", fg="Blue", font=("Helvetica", 18))
        self.label1.place(x=10,y=70)
        self.hops = Label(text="max number of hops :", fg="Blue", font=("Helvetica", 18))
        self.hops.place(x=350, y=130)
        self.hobs1 = Button( text = '1', width = 5 )
        self.hobs1.place(x=350, y=160)
        self.hobs2 = Button( text = '2', width = 5 )
        self.hobs2.place(x=420, y=160)
        self.hobs3 = Button( text = '3', width = 5 )
        self.hobs3.place(x=490, y=160)        
        self.servidores = []
        self.gateways = []
        
        count = 0
        with open("/etc/openvpn/home_voider") as file:
            home = file.read().splitlines()[0]
            file.close()

        localpath = home + '/.config/voider/certs/'

        with open(localpath + 'occupants') as file:
            servers = file.read().splitlines()
            file.close()
        mark = 0
        L1 = []
        for server in servers :
            tmp = count + 2
            self.servidores.append(Label(text='10.' + str(tmp) + '.1.1'))
            self.gateways.append(Button( text = 'blub ' + str(tmp), width = 5, command = lambda m=int(count + 2): self.set_new_gateway(m)))            
            mark = (100 + (count * 30))            
            self.servidores[count].place(x=100, y=mark)            
            self.gateways[count].place(x=270, y=mark)            
            count = copy.deepcopy(count + 1)

        self.label2 = Label(text="clients : ", fg="Blue", font=("Helvetica", 18))
        self.label2.place(x=10,y=mark + 40)

        self.clientes = []
        
        mark = mark + 60
        count = 0
        localpath = home + '/.config/voider/self/'

        with open(localpath + 'occupants') as file:
            clients = file.read().splitlines()
            file.close()
        
        for client in clients :
            self.clientes.append(Label(text='10.1.' + str(count + 2) + '.1'))
            self.clientes[count].place(x=100, y=(mark + (count * 30)))
            count += 1
        
        with open(localpath + 'int_out') as file:
            int_out = file.read().splitlines()
            file.close()

        self.gateway = Label( text = int_out)
        self.gateway.place(x=370, y = 100)        
           
        self.lbl = Label(text="line is hot and ready to start phonecall")
        self.lbl.place(x=300, y=270)
        self.lbl_change()
        
    
    def call_on(self):
        load = Image.open("pics/green.png")
        render = ImageTk.PhotoImage(load)
        self.img = Label(image=render)
        self.img.image = render
        self.img.place(x=570, y=270)
        self.lbl.place(x=300, y=270)
        self.lbl.configure(text="phone call ongoing if this is wrong press REBOOT")

    def call_off(self):
        load = Image.open("pics/red.png")
        render = ImageTk.PhotoImage(load)
        self.img = Label(image=render)
        self.img.image = render
        self.img.place(x=570, y=270)
        self.lbl.place(x=300, y=270)
        self.lbl.configure(text="line is hot and ready to start phonecall")
    
    def set_new_gateway(self, num):
        print(num)
        self.gateways[num - 2].config(relief=SUNKEN)

    def lbl_change(self):
        if(call_started.is_set()):
            self.call_on()
        else:
            self.call_off()
        self.after(1000, self.lbl_change)

    

root = Tk()
app=App(root)
root.title("voider")
root.geometry("600x300")

root.button0 = Button( root, text = "PRESS TO CLOSE", width = 25, command = close_window )
root.button0.grid( row = 1, column = 1, columnspan = 2, sticky = W+E+N+S )
root.button1 = Button( root, text = "REBOOT PATCH ON THE WIRE", width = 25, command = lambda: boot_patch(home, m1, m2, call_started) )
root.button1.grid( row = 0, column = 1, columnspan = 2, sticky = W+E+N+S )

root.resizable(0, 0)
root.after(1000, app.lbl_change)
root.mainloop()


