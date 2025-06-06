# voider_2

![tiefer](tiefer.png)

## Overview

Direct IP Calls, which are IP agnostic.  
SRTP is natively supported by the phones.  
The private phone number on the phone itself is always: **172.16.19.85/30**  
The gateway is always: **172.16.19.86/30**.

_Agnostic in the sense that on the good old phones you did not know who was calling you, because old phones don't have a display. So it's "I got to hear it to believe it." You will see the call incoming from a specific fake IP address, but you may or may not map that to the caller's IP address. Perhaps "anonymous phone calls" is a better term. There is a "do not disturb" feature which you can use; the phone stays quiet and the caller gets a "busy"._

## Disclaimer

- You need to already be using a Linux machine to set this up.
- You need to know how to SSH into a Linux machine to set this up.

After all is done, this Raspberry Pi will be a device to be thought of like the good old phones, as seen in the picture. This Raspberry Pi will be a dedicated machine only for the phone.

## How to Install

1. Flash Alpine Linux:
   ```bash
   dd if=alpine-rpi-3.20.3-aarch64.img of=/dev/sdX bs=4M
   ```

2. Run `setup-alpine`.

3. Set up another user other than root; DHCP on `eth0` is fine.

4. Use the same micro SD card for the OS (type `mmcblk0`).

5. Clone the repository:
   ```bash
   git clone https://github.com/slave-blocker/voider_2.git
   ```

6. Navigate to the directory:
   ```bash
   cd voider/voider
   ```

7. As a user, run:
   ```bash
   doas ./install.sh
   ```

8. As root, run:
   - Let it be WireGuard, let Quad9, no to IPv6, and at the end, don't reboot; the script will do that for you.
   ```bash
   ./install_as_root.sh
   ```

## How to Setup

1. Navigate to the configuration directory:
   ```bash
   cd ~/.config/voider
   ```

2. Choose interfaces:
   - This will set up `/etc/network/interfaces` and then reboot.
   - The phone needs to be connected already with the Raspberry Pi.

   - Run this as a normal user :
   ```bash
   doas ./main.sh
   ```

3. Build the `go-libp2p` executable:
   - Run this as a normal user, and then you will be asked for the `doas` password :
   ```bash
   ./main.sh
   ```

4. After reading "success," you should be good to go.

## How to Use

1. Buy a Grandstream IP phone that has a Direct IP call feature (tested with GXP1610).

2. Install `voider` on a Raspberry Pi or any Linux machine.

3. Connect a Grandstream phone to the USB dongle of your machine.

4. Run:
   ```bash
   doas ./main.sh
   ```
   to create new clients or to connect to servers.

5. Once connections exist to servers or clients, go to the phone and make a DIRECT IP CALL:
   - **Clients:**
     - `10.1.2.1` ---> 1st client
     - `10.1.3.1` ---> 2nd client
     - `10.1.4.1` ---> 3rd client
   - **Servers:**
     - `10.2.1.1` ---> 1st server
     - `10.3.1.1` ---> 2nd server
     - `10.4.1.1` ---> 3rd server

_Out of the box, Grandstream phones should use RTP. To enable SRTP, access your phone's web interface, go to Account -> Audio Settings, and set SRTP to Enabled and Forced._

## Technical Details

There is no PBX being used; instead, SIP packets die before getting to the callee. Then, some deep packet inspection happens, replacing `172.16.19.85` with a fake address. The packet is then replayed, using Scapy and `tcprewrite`, towards the callee phone.

### Note

Golang uses [Go Telemetry](https://go.dev/blog/gotelemetry). To switch that off:
    ```bash
    go telemetry off
    ```

Connecting two devices over `go-libp2p` can sometimes take a lot of time. After two devices have announced themselves long enough over the Kademlia DHT, it is relatively quick to reconnect if your router changes its dynamic IP. The Go executable is around 40 MB in size, and during the search and connect procedure, the listening port of your Raspberry Pi transmits a lot of data.

To check the size of the Go cache, run:
    ```bash
    du -hs $(go env GOCACHE)
    ```
Sometimes this can be up to 341 MB! (The Alpine Linux image is only 90 MB.)

To clean the Go build cache, run:
    ```bash
    go clean -cache
    ```
This will clean `~/.cache/go-build`.

If you are not okay with these aspects of `go-libp2p`, consider using the first version of `voider`.

## Contact

Please do contact me for critiques, suggestions, questions, kudos, and even mobbing attempts are welcome.

- IRC: **monero-pt**

## Special Thanks

Special thanks to Andreas Hein!

A do nation is the best nation!

## MONERO

![xmr](xmr.gif)
