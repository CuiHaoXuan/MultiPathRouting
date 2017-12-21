from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch,Host,OVSSwitch
from mininet.topo import Topo,SingleSwitchTopo
from mininet.log import lg
from mininet.util import irange
from mininet.node import RemoteController,Controller
from functools import partial
from mininet.cli import CLI

import sys

class Link:
    def __init__(self):
        self.node1=None
        self.node2=None
        self.link=None
        self.port1=0
        self.port2=0
    def setlink(self,mnlink):

        self.port1 = self.node1.curPortNum
        self.port2 = self.node2.curPortNum
        self.link=mnlink(self.node1,self.node2,self.port1,self.port2)
        self.node1.curPortNum=self.node1.curPortNum+1
        self.node2.curPortNum=self.node2.curPortNum+1

class Node:
    def __init__(self):
        self.node=None
        self.name=""
        self.link=set()
        self.curPortNum=1
        self.neighbors={}

        self.prevNode = None
        self.nextNode = None

    #these methods for BFS searching
    def getNeighbors(self):
        nb=set()
        for k in self.neighbors.keys():
            nb.add(self.neighbors[k])
        return nb
    def getName(self):
        return self.name
    def connectNode(self,node1):
        self.nextNode=node1
        node1.prevNode=self

class FatTree(Topo):
    def Linking(self,node1,node2):

        port1=node1.curPortNum
        port2=node2.curPortNum
        node1.neighbors[port1]=node2
        node2.neighbors[port2]=node1

        print("add link",node1.name,port1,node2.name,port2)
        try:
            self.addLink(node1.node,node2.node,port1,port2)
        except Exception as e:
            print(e.args)
            print("error adding this link")
        node1.curPortNum=port1+1
        node2.curPortNum=port2+1


    def createBlock(self,index):
        a=[]
        e=[]
        for i in range(self.aggreagationNum):
            aggS=Node()
            aggS.name="a"+str(i)+"_"+str(index)
            ip='10.'+str(index)+'.1.'+str(i+2)
            aggS.node=self.addSwitch(aggS.name,cls=self.AggregationSwitchType)
            self.AllNodes.add(aggS)
            a.append(aggS)
            print("adding aggregation switch",aggS.name)

        for i in range(self.edgeNum):
            edgeS=Node()
            edgeS.name="e"+str(i)+"_"+str(index)
            ip='10.'+str(index)+'.2'+str(i+2)
            edgeS.node=self.addSwitch(edgeS.name,cls=self.EdgeSwitchType)
            self.AllNodes.add(edgeS)
            e.append(edgeS)
            print("adding edge switch",edgeS.name)

            server=Node()
            server.name="server"+str(i)+"_"+str(index)
            ip='10.'+str(index)+'.2'+str(i+2+self.edgeNum)
            server.node=self.addHost(server.name,cls=self.HostType)
            self.AllNodes.add(server)
            print("adding server",server.name)

            link=Link()
            link.node1=server
            link.node2=edgeS
            #link.setlink(self.addLink)
            self.Linking(server,edgeS)

        for i in range(len(a)):
            aggS=a[i]
            for j in range(len(e)):
                edgeS=e[j]
                link = Link()
                link.node1 = aggS
                link.node2 = edgeS
                #link.setlink(self.addLink)
                self.Linking(aggS,edgeS)


        return a

    def buildTopo(self):

        self.coreswitches=[]
        self.block=[]

        print("building net topo")
        for i in range(self.coreNum):
            coreS=Node()
            coreS.name="c"+str(i)
            ip='10.'+str(i)+".0.1"
            coreS.node=self.addSwitch(coreS.name,cls=self.CoreSwitchType)
            self.AllNodes.add(coreS)
            self.block.append(self.createBlock(i))
            self.coreswitches.append(coreS)
            print("adding core Switch",coreS.name)

        for i in range(len(self.coreswitches)):
            coreS=self.coreswitches[i]
            for j in range(len(self.block)):
                aggIndex=i%self.aggreagationNum
                block=self.block[j]
                aggS=block[aggIndex]
                link=Link()
                link.node1=coreS
                link.node2=aggS
                #link.setlink(self.addLink)
                self.Linking(coreS,aggS)

        #add an outer test Router
        router=Node()
        router.name='outerR'
        router.node = self.addHost('outerR',cls=Host)
        self.AllNodes.add(router)
        for i in range(len(self.coreswitches)):
            coreS=self.coreswitches[i]
            self.Linking(router,coreS)

        print("topo init finshed")


    def __init__(self):
        Topo.__init__(self)
        self.coreNum = 3
        self.aggreagationNum = 3
        self.edgeNum = 2

        self.CoreSwitchType = OVSKernelSwitch
        self.AggregationSwitchType = OVSKernelSwitch
        self.EdgeSwitchType = OVSKernelSwitch
        self.HostType = Host
        self.AllNodes=set()

        self.buildTopo()
        #self.test1()


    def test1(self):
        s1 = self.addSwitch('s1',cls=OVSKernelSwitch)
        s2 = self.addSwitch('s2',cls=OVSKernelSwitch)
        h1 = self.addHost('h1',cls=Host)
        h2 = self.addHost('h2',cls=Host)
        h3=self.addHost('h3',cls=Host)
        h4=self.addHost('h4',cls=Host)
        l1=self.addLink(s1, h1,1,1)
        l2=self.addLink(s1, s2,2,2)
        l3=self.addLink(s2, h2,1,2)
        l4=self.addLink(s1,h3,3,0)
        l5=self.addLink(s2,h4,3,0)

topos={'FT':(lambda :FatTree())}
def test():

    net=Mininet(topo=FatTree())#,controller=partial(RemoteController,ip='127.0.0.1',port=6653))
    net.start()
    #print net.hosts
    net.pingAllFull()
    CLI(net)
    net.stop()




def Test(length):
    test()

if __name__ == '__main__':

    lg.setLogLevel('info')
    Test(10)



