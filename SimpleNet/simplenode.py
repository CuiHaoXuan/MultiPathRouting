import Queue
import threading
import time

#net link def
class Link:
    def __init__(self,node1,node2,bw=1000):
        self.node1=node1
        self.node2=node2

        self.port1=-1
        self.port2=-1
        self.bw=bw

    def setlink(self):

        self.port1 = self.node1.curPortNum
        self.port2 = self.node2.curPortNum

        self.node1.neighbors[self.port1] = self.node2
        self.node2.neighbors[self.port2] = self.node1

        print("adding link",self.node1.name,self.port1,self.node2.name,self.port2)

        self.node1.curPortNum=self.node1.curPortNum+1
        self.node2.curPortNum=self.node2.curPortNum+1

        self.node1.link.add(self)
        self.node2.link.add(self)


#net nodes def
class Node(threading.Thread):
    def __init__(self,pf=100,capacity=-1):
        threading.Thread.__init__(self)
        self.name=""
        self.link=set()
        self.curPortNum=0
        self.neighbors={}

        self.prevNode = None
        self.nextNode = None

        self.cost=0#measures by the que length
        self.que=Queue.Queue(capacity)

        self.ForwardingTable=set()
        self.performance=pf
        self.working=True
        self.com=threading.Condition()
    def run(self):
        while self.working:
            if self.que.qsize() <= 0:
                self.com.wait()
            pkt=self.que.get()
            time.sleep(pkt.dataSize/self.performance)
            self.forward(pkt)


    def forward(self,pkt):
        dataID=pkt.id
        frd=False
        for rule in self.ForwardingTable:
            if rule.dataID==dataID:
                nextNode=rule.nextNode
                for link in self.link:
                    if link.node1.name==self.name:
                        nb=link.node2
                    else:
                        nb=link.node1

                    if nb.name==nextNode:
                        time.sleep(pkt.dataSize / link.bw)
                        nb.cacheData(pkt)
                        frd=True
                break
        if frd==False:
            self.drop(pkt)
            print("no matching rule found,drop package")
        pass

    def drop(self,pkt):
        prevNode=pkt.Src
        drp=False
        for link in self.link:
            if link.node1.name == self.name:
                nb = link.node2
            else:
                nb = link.node1

            if nb.name == prevNode:
                time.sleep(pkt.dataSize / link.bw)
                nb.cacheData(pkt)
                drp = True
                print("drop package and host get reponse")
                break
        if drp==False:
            print("Inner Error, Still Drop package,But Host get no reponse.")

    def cacheData(self,pkt):

        if self.que.maxsize==self.que.qsize():
            self.drop(pkt)
        else:
            self.que.put(pkt)

    def getNeighbors(self):
        nb=set()
        for k in self.neighbors.keys():
            nb.add(self.neighbors[k])
        return nb

    def connectNode(self,node1):
        self.nextNode=node1
        node1.prevNode=self
#net data def
class PktData:
    def __init__(self):
        self.dataSize=2
        self.Src=''
        self.Dst=''
        self.id=''
        self.seq=1
        self.total=1

class FlowRule:
    def __init__(self):
        self.dataID=''
        self.nextNode=''



