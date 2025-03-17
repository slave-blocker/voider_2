#!/bin/bash

home="/home/"$(hostname)"/"

intin=$home".config/voider/self/int_in"

if [[ ! -e $intin ]]
    then
    echo "Incoming interface not defined, the one connected to the phone ."
    ls "/sys/class/net"
    echo "Please type one from the above list :"
    read int_in
    echo -n $int_in > $intin 
fi

intout=$home".config/voider/self/int_out"

if [[ ! -e $intout ]]
    then
    echo "Outgoing interface not defined, the one directed to the internet ."
    ls "/sys/class/net"
    echo "Please type one from the above list :"
    read int_out
    echo -n $int_out > $intout 
fi

localip=$home".config/voider/self/localip"

if [[ ! -e $localip ]]
    then
    echo "setting a permanent lan ip, with dhcp"
    echo "checking for a connection, pinging google"    
    ping -c 1 8.8.8.8                    
    if [[ $? -eq 0 ]]       
        then
        echo "assuming "$(cat $intout)" is connected to the internet"
        lanip=$(ip -f inet addr show $(cat $intout) | awk '/inet / {print $2}')    

        sed -i "s%§0%$(cat $intout)%g" $home".config/voider/self/interfaces"        
        sed -i "s%§1%$(cat $intin)%g" $home".config/voider/self/interfaces"        
        sed -i "s%§2%address\ $lanip%g" $home".config/voider/self/interfaces"

        lanip=$(ip -f inet addr show $(cat $intout) | sed -En -e 's/.*inet ([0-9.]+).*/\1/p')    

        echo -n $lanip > $localip

        doas mv $home".config/voider/self/interfaces" "/etc/network/interfaces"
        echo " making changes to the interfaces permanent, rebooting ..."
        doas reboot
        exit 1   
    else
        echo "Please get an ip address over dhcp for "$(cat $intout)
        exit 1   
    fi
fi

setsrcport () {
    while true
        do
        try_random=$RANDOM
        if [[ $try_random -gt 1024 ]]
            then
            busy=$(doas netstat -tulpn | grep $try_random | wc -l)
            if [[ $busy -eq 0 ]]
                then                                    
                echo -n $try_random > /home/$(hostname)/.config/voider/punchit/rndsrcport
                break
            fi                    
        fi
    done
}

#run this as user without doas
go_bin=$home".config/voider/punchit/punchit"

if [[ ! -e $go_bin ]]
    then
    if [[ $EUID == 0 ]]
        then
        echo "run this part without doas"
        exit 1
    else    
        echo "building go-libp2p executable"
        cd $home".config/voider/punchit"
        go build
        if [[ ! -e $go_bin ]]
            then
            echo "something went wrong..."
            exit 1    
        else
            echo "success..."
            echo "run once to create self private key"        
            /home/$(hostname)/.config/voider/punchit/punchit 1>/dev/null 2>/dev/null
            echo "run again to create hostid file, now doas required ..."
            setsrcport        
            /home/$(hostname)/.config/voider/punchit/punchit 1>/dev/null 2>/dev/null        
            if [[ ! -e /home/$(hostname)/.config/voider/punchit/hostid ]]
                then 
                echo "creating the hostid file went wrong..."
                exit 1    
            fi        
        fi
    fi
fi

if [[ $EUID != 0 ]]
    then
    echo "run this part with doas"
    exit 1
fi

echo "choose option :"

echo "to quit - just press enter."
echo "1 - call pivpn, to add a client connection to this server"
echo "2 - call pivpn, to revoke a client connection to this server"
echo "3 - create a client connection to another server"
echo "4 - delete a client connection to another server"
echo "5 - show own libp2p host id"
#TODO echo "6 - shutdown entire network routing protocol"


read option

if [[ $option -eq 1 ]]
    then

    echo "Please copy paste the libp2p peerid of the client:"

    read peerid

    if [[ -z $peerid ]]
        then
        echo "Please try again"
        exit
    fi

    pivpn -a

    #this line is crucial since the wireguard server needs to let 172.29.0.0/16 pass.

    lines=$(cat /etc/wireguard/wg0.conf | wc -l)    
    lines=$(( $lines - 1 ))   
    #this always works because wireguard appends its clients to wg0.conf
    crucial=$(echo  $(sed "$lines q;d" /etc/wireguard/wg0.conf ), 172.29.0.0/16)
    sed -i "$lines s?.*?$crucial?" /etc/wireguard/wg0.conf
    wg-quick down wg0
    wg-quick up wg0
    
    certdotconf=$(ls /home/$(hostname)/configs)

    str=$(sed "3 q;d" /home/$(hostname)/configs/$certdotconf)
    str2=$(echo $str | sed 's/\/.*//')
    client_idx=$(echo $str2 | awk -F'.' '{print $4}')

    sed -i "$client_idx s/.*/1/" /home/$(hostname)/.config/voider/clients/occupants 
    mkdir /home/$(hostname)/.config/voider/clients/clients/$client_idx
    mkdir /home/$(hostname)/.config/voider/clients/clients/$client_idx/cert/

    rm -rf /home/$(hostname)/.config/voider/new_client/
    mkdir /home/$(hostname)/.config/voider/new_client/

    mv /home/$(hostname)/configs/$certdotconf /home/$(hostname)/.config/voider/new_client/
    echo "PersistentKeepalive = 5" >> /home/$(hostname)/.config/voider/new_client/$certdotconf
    echo "#$(cat /home/$(hostname)/.config/voider/punchit/hostid)" >> /home/$(hostname)/.config/voider/new_client/$certdotconf
    
    cp /home/$(hostname)/.config/voider/new_client/$certdotconf /home/$(hostname)/.config/voider/clients/clients/$client_idx/cert/

    sed -i "$client_idx s/.*/$peerid/" /home/$(hostname)/.config/voider/clients/client_ids

fi

if [[ $option -eq 2 ]]
    then
    echo "Please choose x ( 2<= x <= 254), to remove phone number : 10.1.x.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/clients/occupants)
    
    if [[ $str -eq "0" ]]
        then
        echo "Phone number does not exist"
        exit
    else    
        #this directory only contains one file :
        certdotconf=$(ls /home/$(hostname)/.config/voider/clients/clients/$x/cert/)
        client_name=$(echo $certdotconf | sed 's/\..*//')
        pivpn -r $client_name -y
        rm -rf /home/$(hostname)/.config/voider/clients/clients/$x
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/clients/occupants
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/clients/client_ids
        echo "phone number deleted."    
    fi
fi

if [[ $option -eq 3 ]]
    then
    echo "Please place the client cert into the folder \"new_server\" "
    echo "Press enter when done."
    read

    certdotconf=$(ls /home/$(hostname)/.config/voider/new_server)

    if [[ -z $certdotconf ]]
        then
        echo "Please try again"
        exit
    fi

    echo "Please choose x ( 2<= x <= 254) with which number to call : 10.x.1.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/servers/occupants)
    
    if [[ $str -ne "0" ]]
        then
        echo "Phone number already taken"
        exit
    fi

    sed -i "$x s/.*/1/" /home/$(hostname)/.config/voider/servers/occupants 
    mkdir /home/$(hostname)/.config/voider/servers/servers/$x/
    mkdir /home/$(hostname)/.config/voider/servers/servers/$x/cert/
    mv /home/$(hostname)/.config/voider/new_server/$certdotconf /home/$(hostname)/.config/voider/servers/servers/$x/cert/

    last=$(cat /home/$(hostname)/.config/voider/servers/servers/$x/cert/$certdotconf | wc -l)
    peerid=$(sed "$last q;d" /home/$(hostname)/.config/voider/servers/servers/$x/cert/$certdotconf)
    sed -i "$x s/.*/${peerid:1}/" /home/$(hostname)/.config/voider/servers/server_ids

    echo "phone number added."

fi

if [[ $option -eq 4 ]]
    then
    echo "Please choose x ( 2<= x <= 254), to remove phone number : 10.x.1.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/servers/occupants)
    
    if [[ $str -eq "0" ]]
        then
        echo "Phone number does not exist"
        exit
    else    
        rm -rf /home/$(hostname)/.config/voider/servers/servers/$x
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/servers/occupants
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/servers/server_ids
        echo "phone number deleted."    
    fi
fi

if [[ $option -eq 5 ]]
    then
    cat /home/$(hostname)/.config/voider/punchit/hostid
    echo " "
fi

