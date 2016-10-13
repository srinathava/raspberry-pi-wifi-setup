# WiFi setup script for a headless Raspberry Pi device

This setup shows a recipe for being able to set the WiFi password for a Raspberry Pi which is "headless", 
i.e., not connected to a monitor/keyboard. Something like this would be useful if you plan to "ship" a 
headless Raspberry Pi device and let a user set it up after they receive it.

When a "customer" first receives such a device, he would do something like:

- Download the following [zip file](https://github.com/srinathava/raspberry-pi-wifi-setup/archive/master.zip).
- Unzip it using any standard unzip tool.
- Open web/setup.html from the archive in a reasonably modern browser (Chrome/Safari/Firefox) and follow the instructions in there.
- As part of following the instructions, the user is instructed to connect the device once using an 
ethernet cable to the router physically. This allows the device to connect to the local network without
needing a Wifi password.

NOTE: I initially had the idea that the user could just visit a web-site hosted outside the local network and 
make Javascript contained in that web-site scan the local network for an open websocket connection. That however
just does not work becuase most modern browsers prevent cross-domain content loading.

## Raspberry Pi setup for "device vendor"
In order to create a Rapsberry Pi which can offer such a workflow for a user, the device creator needs to set
up the Raspberry Pi as follows:

- Update Python with autobahn:
        
        pip install autobahn
        
- Download this repo:
  
        git clone https://github.com/srinathava/raspberry-pi-wifi-setup.git
        
- Modify /etc/rc.local to run the websocket server as part of the boot sequence. Use your favorite editor to include the following in that file:
       
       python /home/pi/raspberry-pi-wifi-setup/server.py
       
