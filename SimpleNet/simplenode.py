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
                self.com.acquire()
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
            self.getDropResponse(pkt)
            print("no matching rule found,drop package")
        pass

    def getDropResponse(self,pkt):
        prevNode=pkt.prevHop
        drp=False
        for link in self.link:
            if link.node1.name == self.name:
                nb = link.node2
            else:
                nb = link.node1

            if nb.name == prevNode:
                time.sleep(pkt.dataSize / link.bw)
                for ack in self.waitAck:
                    if ack.id == pkt.id and ack.seq == pkt.seq:
                        nb.getDropResponse(ack)
                        self.waitAck.remove(ack)
                        drp = True

                        break
                print("drop package and host get reponse")
                break
        if drp==False:
            print("Inner Error, drop pkt!!!")

    def cacheData(self,pkt):

        if self.que.maxsize==self.que.qsize():
            self.getDropResponse(pkt)
        else:
            self.que.put(pkt)


    def getReceivedAck(self,pkt):
        prevNode = pkt.prevHop
        drp = False
        for link in self.link:
            if link.node1.name == self.name:
                nb = link.node2
            else:
                nb = link.node1

            if nb.name == prevNode:
                time.sleep(pkt.dataSize / link.bw)
                for ack in self.waitAck:
                    if ack.id == pkt.id and ack.seq == pkt.seq:
                        nb.getReceivedAck(ack)
                        self.waitAck.remove(ack)
                        drp=True

                        break
                print("ack receive package and host get reponse")
                break
        if drp==False:
            print("Inner Error, ACK rcv pkt!!!")

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
    def __init__(self,role='Sender',pf=10,capacity=-1,controller=None):
        Node.__init__(self,pf=pf,capacity=capacity)
        self.role=role
        self.controller=None
        if self.role=='Sender':
            self.controller=controller

    def reset(self):
        self.que=Queue.Queue()
        self.working=True
        self.waitAck=set()

    def prepareData(self,pktsize=100,totalsize=10000,id='',src='',dst=''):
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



    def sendPkt(self,pkt):
        self.forward(pkt)

        pass
    def receivePkt(self,pkt):
        self.cacheData(pkt)
        pass
    def run(self):
        if self.role=='Sender':
            while self.working:
                if self.que.qsize() <= 0:
                    self.working=False
                    print("sender",self.name,"finished sending all pkts")
                pkt = self.que.get()
                time.sleep(pkt.dataSize / self.performance)
                self.sendPkt(pkt)
        elif self.role=='Receiver':
            total=100000
            while self.working:
                if self.que.qsize()>=total:
                    self.working=False
                    print("receiver",self.name,"finished receiving all pkts")
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
        pkt1=PktData(id=pkt.id,seq=pkt.seq,size=pkt.dataSize)
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



