#!/usr/bin/python

"""
mininet_tsq.py: Simple example of MPTCP in Mininet to illustrate emulation pitfalls.

Check https://progmp.net/mininetPitfalls.html for more details.

"""

import os
from time import sleep
from threading import Thread
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import RemoteController
import mininet.util as util


class VideoThread(Thread):
    def __init__(self, hn, cmd):
        self.hostnum = hn
        self.command =cmd
        Thread.__init__(self)
        
    def run(self):
        self.hostnum.cmd(self.command)


class StaticTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        self.addLink(h1, s1, bw=100)
        self.addLink(h2, s1, bw=100)
        
        self.addLink(h1, s2, bw=100)
        self.addLink(h2, s2, bw=100)
        # if 0 == 1:
        #     self.addLink(h1, s1, bw=100, delay="20ms")
        #     self.addLink(h2, s1, bw=100, delay="20ms")
        #     self.addLink(h1, s2, bw=100, delay="10ms")
        #     self.addLink(h2, s2, bw=100, delay="10ms")
        #
        # else:


def runExperiment():
    # c = RemoteController('c0', ip='0.0.0.0', port=6633)
    
    net = Mininet(topo=StaticTopo())
    net.start()
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # there is probably a better way, but somehow we have to configure
    # the IP addresses
    for i in range(0, 2):
        h1.cmd('ifconfig h1-eth' + str(i) + ' 1' + str(i) + '.0.0.1')
        h2.cmd('ifconfig h2-eth' + str(i) + ' 1' + str(i) + '.0.0.2')
    
    # set path manager
    os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh')
    # set scheduler
    os.system('sysctl -w net.mptcp.mptcp_scheduler=rbs')
    
    # you may want to start wireshark here and finish by typing exit
    cli = CLI(net)
    CLI.do_xterm(cli, 'h1 h2')
    CLI(net)
    h1.cmd('ffplay -rtsp_flags listen rtsp://{}:6633/live.sdp?tcp 2>listener.txt &'.format('0.0.0.0'))
    sleep(3)
    h2.cmd("ffmpeg -i ./videos/sample2.mp4 -f rtsp -rtsp_transport tcp rtsp://{}:6633/live.sdp 2>vid.txt".format(h1.IP()))
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('warning')
    # enable MPTCP
    os.system('sysctl -w net.mptcp.mptcp_enabled=1')
    # enable debug output, execute "dmesg" to read output
    os.system('sysctl -w net.mptcp.mptcp_debug=0')
    
    runExperiment()
