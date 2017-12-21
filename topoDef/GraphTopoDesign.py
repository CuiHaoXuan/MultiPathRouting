#graph topology design
from mininet.net import Mininet
from mininet.node import UserSwitch, OVSKernelSwitch
from mininet.topo import Topo
from mininet.log import lg
from mininet.util import irange
from mininet.node import RemoteController
from functools import partial
from mininet.cli import CLI

import sys

class node:


    def __init__(self,name):
        self.__name=name
        self.__neighbors = set()
        self.prevNode = None
        self.nextNode = None

    def getName(self):
        return self.__name
    def connectNode(self,node1):
        self.nextNode=node1
        node1.prevNode=self
    def addNeighbor(self,node1):
        #print(self.__name, len(self.__neighbors), 'add', node1.getName(), len(node1.getNeighbors()))
        self.__neighbors.add(node1)
        #print(len(self.__neighbors), len(node1.getNeighbors()))

    def getNeighbors(self):
        return self.__neighbors

class Graph:
    linkCount=0

    def addneighbor2(self,node1,node2):

        #print '---before'
        #print '----neighbors of node1:', node1.getName()
        #for n in node1.getNeighbors():
        #    print(n.getName())
        #print '----neighbors of node2:', node2.getName()
        #for n in node2.getNeighbors():
        #    print n.getName()

        #print 'add link', node1.getName(), node2.getName()
        node1.addNeighbor(node2)
        node2.addNeighbor(node1)
        self.linkCount=self.linkCount+1

        #print len(node1.getNeighbors()), len(node2.getNeighbors())

        #print '----neighbors of node1:', node1.getName()
        #for n in node1.getNeighbors():
        #    print(n.getName())
        #print '----neighbors of node2:', node2.getName()
        #for n in node2.getNeighbors():
        #    print n.getName()
        #print 'link and node block end'



class FatTree(Graph):
    def __init__(self):
        self.c = []
        self.a = []
        self.s = []
        self.h = []
        '''make sure that nc%na==0'''
        self.nc = 10  # total core switch
        self.na = 5  # aggregation switch in one block
        self.ns = 8  # edge switch in one block
        self.nh = 6  # host connected to each edge switch
        self.midblock={}#middle block area

    def addblock(self,anodes,snodes):
        for a in anodes:
            for s in snodes:
                self.addneighbor2(a,s)

    def createBlock(self,index):
        a=[]
        s=[]
        h=[]
        m=self.na
        n=self.ns

        for i in range(m):
            anode=node('aggregation_'+str(index+1)+'_'+str(i+1))
            a.append(anode)

        for i in range(n):
            snode=node('edge_'+str(index+1)+'_'+str(i+1))
            s.append(snode)
            h=[]
            for j in range(self.nh):
                hnode=node('host_'+str(index+1)+'_'+str(i+1)+'_'+str(j+1))
                h.append(hnode)
                self.addneighbor2(s[i],h[j])
                self.h=self.h+h

        self.addblock(a, s)
        self.midblock[index] = a
        self.a=self.a+a
        self.s=self.s+s

    def generateTopo(self):

        for i in range(self.nc):
            self.c.append(node('core'+str(i+1)))
            self.createBlock(i)

        for i in range(self.nc):
            k=i%self.na
            for j in range(self.nc):
                self.addneighbor2(self.c[j],self.midblock[i][k])
                pass

#test
if __name__=="__main__":
    ftree=FatTree()
    ftree.generateTopo()
    print "FatTree,linkCount=", ftree.linkCount
    #exit(0)

    for c in ftree.c:
        for a in c.getNeighbors():
            print len(c.getNeighbors()),'neighbors of', c.getName(),'is',a.getName()
            for s in a.getNeighbors():
                print len(a.getNeighbors()),'neighbor of ',a.getName(),'is',s.getName()
                for h in s.getNeighbors():
                    print len(s.getNeighbors()),'neighbor of',s.getName(),'is',h.getName()
                    pass
    print "----------"
    for i in ftree.s:
        print i.getName()



