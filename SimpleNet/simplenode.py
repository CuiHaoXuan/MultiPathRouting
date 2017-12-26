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
com=threading.Condition()

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
        self.sndtime=None
        self.rcvtime=None
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
        return pkt1

#net flow rule def
class FlowRule:
    def __init__(self):
        self.dataID=''
        self.nextNode=''
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
        self.capacity=capacity
        self.working=True
        self.com=threading.Condition()

    def run(self):

        com.acquire()
        print(self.name,"is running")
        com.release()

        while self.working:
            if self.que.qsize() <= 0:
                #com.acquire()
                #print(self.name, "is waiting due to que size=0")
                #com.release()

                self.com.acquire()
                self.com.wait()
                #com.acquire()
                #print(self.name, "wake up")
                #com.release()

            pkt=self.que.get()
            time.sleep(pkt.dataSize/self.performance)
            self.forward(pkt)
    def cachaeSize(self):
        sum=0
        for pkt in self.que.queue:
            sum=sum+pkt.dataSize
        return sum
    def cacheData(self,pkt):

        if self.capacity>0 and self.capacity<=self.cachaeSize():
            com.acquire()
            print(self.name, "cachaed full(%d),drop pkt ----------->"%(self.cachaeSize()), pkt.id, pkt.seq, pkt.total)
            com.release()
            self.getDropResponse(pkt)
        else:
            #com.acquire()
            #print(self.name, "cachaed data", pkt.id, pkt.seq, pkt.total, "into que")
            #com.release()

            self.com.acquire()
            tag=True
            for pkt1 in self.que.queue:
                if pkt1.id==pkt.id and pkt1.seq==pkt.seq:
                    tag=False
                    break
            if tag:
                self.que.put(pkt)
            else:
                com.acquire()
                print(pkt.id,pkt.seq,pkt.total,"already in queue")
                com.release()
            self.com.notifyAll()
            self.com.release()


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

                break
        if frd==False:
            self.getDropResponse(pkt)
            #com.acquire()
            #print("no matching rule found,drop package")
            #com.release()
        pass

    def getDropResponse(self,pkt):
        drp = False
        rm = None
        self.com.acquire()
        for ack in self.waitAck:

            if ack.id == pkt.id and ack.seq == pkt.seq:
                drp = True
                rm = ack
                break
        self.com.release()
        if drp:
            self.com.acquire()
            self.waitAck.remove(rm)
            self.com.release()

            com.acquire()
            print(self.name, "drop receive package", pkt.id, pkt.seq, pkt.total, "and host get reponse")
            com.release()

            prevNode = rm.prevHop

            for link in self.link:
                if link.node1.name == self.name:
                    nb = link.node2
                else:
                    nb = link.node1

                if nb.name == prevNode:
                    time.sleep(pkt.dataSize / link.bw)

                    nb.getDropResponse(rm)

                    break

        else:
            com.acquire()
            print(self.name, "Inner Error, drop rcv pkt!!!", pkt.id, pkt.seq, pkt.total)
            com.release()

    def getReceivedAck(self,pkt):
        drp=False
        rm=None

        self.com.acquire()
        for ack in self.waitAck:
            #print("test",ack,pkt)
            if ack.id == pkt.id and ack.seq == pkt.seq:
                drp = True
                rm = ack
                break
        self.com.release()

        if drp:
            self.com.acquire()
            self.waitAck.remove(rm)
            self.com.release()

            #com.acquire()
            #print(self.name, "ack receive package", pkt.id, pkt.seq, pkt.total, "and host get reponse")
            #com.release()

            prevNode=rm.prevHop

            for link in self.link:
                if link.node1.name == self.name:
                    nb = link.node2
                else:
                    nb = link.node1

                if nb.name == prevNode:
                    time.sleep(pkt.dataSize / link.bw)

                    nb.getReceivedAck(rm)

                    break

        else:
            com.acquire()
            print(self.name,"Inner Error, ACK rcv pkt!!!",pkt.id,pkt.seq,pkt.total)
            com.release()

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
        self.controller=None

        self.sendDict={}
        self.receiveDict={}


    def reset(self):
        self.que=Queue.Queue()
        self.working=True
        self.waitAck=set()
        self.sendDict={}
        self.receiveDict={}

    def requestID(self,dst):
        #get id and generate routing
        return self.controller.generatePktID(self.name,dst)


    def prepareData(self,pktsize=100,totalsize=10000,dst=''):

        id=self.requestID(dst)
        n=totalsize//pktsize
        lastpktsize=0
        if n*pktsize<totalsize:
            lastpktsize=totalsize-lastpktsize
            n=n+1

        self.sendDict[id]=set()
        for i in range(1,n):
            pkt=PktData(id=id, seq=i, size=pktsize)
            pkt.prevHop=self.name
            pkt.Dst=dst
            pkt.Src=self.name
            pkt.total=n
            self.cacheData(pkt)
            self.sendDict[id].add(pkt)

        pkt = PktData(id=id, seq=n, size=lastpktsize)
        pkt.prevHop = self.name
        pkt.Dst = dst
        pkt.Src = self.name
        pkt.total = n
        self.cacheData(pkt)
        self.sendDict[id].add(pkt)

        print("data pkt",id,n)

        self.com.acquire()
        self.com.notify()
        self.com.release()

    def checkSent(self):
        finishList=set()
        for k in self.sendDict.keys():
            if len(self.sendDict[k])==0:
                finishList.add(k)

        return finishList

    def checkReceived(self):
        finishList = set()
        for k in self.receiveDict.keys():
            for pkt in self.receiveDict[k]:
                if len(self.receiveDict[k]) == pkt.total:
                    finishList.add(k)

                break
        if len(finishList)>0:
            with open("../RunLogs/pktTimeLog-"+self.name+".txt","a") as f:
                f.write("===============================\n")
                for k in finishList:
                    f.write(k+"\n")
                    for pkt in self.receiveDict[k]:
                        s=str(pkt.sndtime)+","+str(pkt.rcvtime)+","+str(pkt.rcvtime-pkt.sndtime)
                        f.write(s+"\n")

                f.write("---------------------\n")


        return finishList

    def sendPkt(self,pkt):
        pkt.sndtime=time.time()
        self.forward(pkt)
        self.sendDict[pkt.id].remove(pkt)

        #com.acquire()
        #print(self.name,"send pkt",pkt.id,pkt.seq,pkt.total)
        #com.release()

    def receivePkt(self,pkt):
        pkt.rcvtime=time.time()
        self.waitAck.add(pkt)
        if pkt.id not in self.receiveDict.keys():
            self.receiveDict[pkt.id]=set()
        self.receiveDict[pkt.id].add(pkt)

        self.getReceivedAck(pkt)

        #com.acquire()
        #print(self.name,"receive pkt",pkt.id,pkt.seq,pkt.total)
        #com.release()

    def run(self):

        if self.role=='Sender':
            com.acquire()
            print(self.name,"is sending")
            com.release()
            while self.working:
                if self.que.qsize() <= 0:
                    #com.acquire()
                    #print("sender", self.name, "finished sending all pkts in current cache,now waiting")
                    #com.release()

                    self.com.acquire()

                    self.com.wait()
                    self.com.release()
                    #com.acquire()
                    #print(self.name, "wake up")
                    #com.release()

                pkt = self.que.get()
                time.sleep(pkt.dataSize / self.performance)
                self.sendPkt(pkt)
                fl=self.checkSent()
                if len(fl)>0:
                    for pktID in fl:
                        self.sendDict.pop(pktID)

                        com.acquire()
                        print("sender", self.name, "finished sending all pkts in of pkt id=", pktID)
                        com.release()

        elif self.role=='Receiver':
            com.acquire()
            print(self.name,"is listening for data")
            com.release()

            count=0
            while self.working:
                if self.que.qsize()<=0:
                    #com.acquire()
                    #print("receiver", self.name, "finished receiving all pkts in cache,now waiting")
                    #com.release()

                    self.com.acquire()

                    self.com.wait()
                    self.com.release()
                    #com.acquire()
                    #print(self.name,"wake up")
                    #com.release()

                pkt=self.que.get()
                time.sleep(pkt.dataSize / self.performance)
                self.receivePkt(pkt)

                fl=self.checkReceived()
                if len(fl)>0:
                    for pktID in fl:
                        self.receiveDict.pop(pktID)
                        self.controller.releasePktID(pktID)
                        count=count+1
                        if count>3:
                            exit(10)
                        com.acquire()
                        print("receiver", self.name, "finished receiving all pkts in of pkt id=",pktID)
                        com.release()


    def getDropResponse(self,pkt):
        if self.role=='Receiver':
            super(Server, self).getDropResponse(pkt=pkt)

            return

        rm=None
        self.com.acquire()
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                rm=ack
                break
        self.waitAck.remove(rm)
        self.com.release()
        self.forward(rm)

        com.acquire()
        print("sender",self.name,"caught drop and resend",pkt.id,pkt.seq,pkt.total)
        com.release()


    def getReceivedAck(self,pkt):
        if self.role=='Receiver':
            super(Server, self).getReceivedAck(pkt=pkt)

            return
        self.com.acquire()
        rm=None
        for ack in self.waitAck:
            if ack.id==pkt.id and ack.seq==pkt.seq:
                rm=ack
                break
        self.waitAck.remove(rm)
        self.com.release()

        #com.acquire()
        #print("sender",self.name,"Ack received",pkt.id,pkt.seq,pkt.total)
        #com.release()
        with open("../RunLogs/pktLostLog-"+self.name+".txt","a") as f:
            s=pkt.id+","+str(pkt.seq)+","+str(pkt.total)+"\n"
            f.write(s)







