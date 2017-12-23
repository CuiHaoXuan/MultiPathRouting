import Queue
import threading
import time
'''
this file define the basic function of a simple nework, the assumptions are:
1. each package lost can be infromed
2. node perfromance affect its transfer speed
3. link capacity canont be feed full
4.link bw affect spread speed on the link
'''


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


#net switch-nodes def
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
        self.waitAck=set()

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
                        self.waitAck.add(pkt.copyPktHeader(pkt))
                        pkt.prevHop=self.name
                        nb.cacheData(pkt)
                        frd=True
                break
        if frd==False:
            self.drop(pkt)
            print("no matching rule found,drop package")
        pass

    def getDropResponse(self,pkt):
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                self.drop(ack)
                self.waitAck.remove(ack)
                break
    def getReceivedAck(self,pkt):
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                self.getReceivedAck(ack)
                self.waitAck.remove(ack)
                break
        pass
    def drop(self,pkt):
        prevNode=pkt.prevHop
        drp=False
        for link in self.link:
            if link.node1.name == self.name:
                nb = link.node2
            else:
                nb = link.node1

            if nb.name == prevNode:
                time.sleep(pkt.dataSize / link.bw)
                nb.getDropResponse(pkt)
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

    #these functions are used for seach the graph
    def getNeighbors(self):
        nb=set()
        for k in self.neighbors.keys():
            nb.add(self.neighbors[k])
        return nb

    def connectNode(self,node1):
        self.nextNode=node1
        node1.prevNode=self

#define seaver
class Server(Node):
    def __init__(self,role='Sender',pf=10,capacity=-1):
        Node.__init__(self,pf=pf,capacity=capacity)
        self.role=role
    def prepareData(self,pktsize,totalsize,id,src,dst):
        n=0
        n=totalsize//pktsize
        lastpktsize=0
        if n*pktsize<totalsize:
            lastpktsize=totalsize-lastpktsize
            n=n+1

        for i in range(n-1):
            pkt=PktData(id=id, seq=i, size=pktsize)
            pkt.prevHop=self.name
            pkt.Dst=dst
            pkt.Src=src
            pkt.total=n
            self.cacheData(pkt)
        if lastpktsize>0:
            pkt = PktData(id=id, seq=n-1, size=lastpktsize)
            pkt.prevHop = self.name
            pkt.Dst = dst
            pkt.Src = src
            pkt.total = n
            self.cacheData(pkt)

        pass
    def sendPkt(self,pkt):
        self.forward(pkt)
        pass
    def receivePkt(self,pkt):
        pass
    def run(self):
        if self.role=='Sender':
            while self.working:
                if self.que.qsize() <= 0:
                    self.working=False
                pkt = self.que.get()
                time.sleep(pkt.dataSize / self.performance)
                self.sendPkt(pkt)
        elif self.role=='Receiver':
            total=100000
            while self.working:
                if self.que.qsize()>=total:
                    self.working=False
                pkt=self.que.get()
                time.sleep(pkt.dataSize / self.performance)
                self.receivePkt(pkt)


    def getDropResponse(self,pkt):
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                self.waitAck.remove(ack)
                self.forward(ack)

                break
    def getReceivedAck(self,pkt):
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                self.waitAck.remove(ack)
                break
#def net controller
class Controller:
    def __init__(self,topo):
        self.Topo=None
        self.ID_pool=set()
    def begin(self):
        nodes=self.Topo.AllNodes
        for node in nodes:
            node.start()

    def SearchRoute(self):
        route=[]

        return route

    def SetFlowRule(self,route):
        #route is a list descibe routing from src to dst
        pass
    def generatePktID(self):
        id=''

        return id

#net package def
class PktData:
    def __init__(self,id,seq,size):
        self.dataSize=size
        self.Src=''
        self.Dst=''
        self.prevHop=''
        self.id=id
        self.seq=seq
        self.total=1
        #in my expemeriment, this field is never used
        self.data=None
    def copyPktHeader(self,pkt):
        pkt1=PktData()
        pkt1.dataSize=pkt.dataSize
        pkt1.Src=pkt.Src
        pkt1.Dst=pkt.Dst
        pkt1.prevHop=pkt.prevHop
        pkt1.id=pkt.id
        pkt1.seq=pkt.seq
        pkt1.total=pkt.total


#net flow rule def
class FlowRule:
    def __init__(self):
        self.dataID=''
        self.nextNode=''



