# MPTCP Video Streaming using FFMPEG
## Test setup using Native install of Mininet of Multipath Kernel
## It is assumed that you have installed in FFMPEG in our machine
### Instructions to Run the code
#### `sudo python3 mininet_run.py` 
##### We used python3, as our mininet was installed in python3, user may use any python version
1. On running above command a mininet CLI will be opened, press exit.
2. Now two xterm terminals will be opened one saying node-h1 and other with node-h2
   - In terminal with node h1 run `python3 server.py 0.0.0.0`
   - In terminal with node h2 run `python3 client.py 10.0.0.1`
3. Record the MPTCP packets in Wireshark
4. Then go back to gnome terminal and press exit once again to close xterm terminals and exit the code


##### Video can be paused by pressing the Space Bar 
