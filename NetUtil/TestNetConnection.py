from mininet.net import Mininet
from mininet.log import lg
from mininet.node import RemoteController
from functools import partial
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.clean import cleanup
from topoDef.MininetFatTreeTopo import *

def test():
    try:
        net=Mininet(topo=FatTree(),controller=RemoteController,ipBase='10.0.0.1/8')
        ctr=net.addController('ODL',controller=partial(RemoteController,ip='192.168.3.179/24',port=6633))
        ctr.start()
        net.start()

        #print net.hosts
        net.pingAllFull()
        print(ctr.intfList())
        CLI(net)
        net.stop()
    except Exception or KeyboardInterrupt as e:
        print e
        cleanup()

if __name__ == '__main__':

    lg.setLogLevel('info')
    test()
