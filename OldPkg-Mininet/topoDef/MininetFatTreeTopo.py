from mininet.node import OVSSwitch,Host
from mininet.topo import Topo

#net nodes def
class Node:
    def __init__(self):
        self.node=None
        self.name=""
        self.link=set()
        self.curPortNum=1
        self.neighbors={}

        self.prevNode = None
        self.nextNode = None

        self.cost=0#measures by the que length

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
    #link two nodes
    def Linking(self,node1,node2):

        port1=node1.curPortNum
        port2=node2.curPortNum
        node1.neighbors[port1]=node2
        node2.neighbors[port2]=node1

        #print("add link",node1.name,port1,node2.name,port2)
        try:
            self.addLink(node1.node,node2.node,port1,port2)
        except Exception as e:
            print(e.args)
            print("error adding this link")
        node1.curPortNum=port1+1
        node2.curPortNum=port2+1

    #build block of edge and aggreagation switches
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
            #print("adding aggregation switch",aggS.name)

        for i in range(self.edgeNum):

            edgeS=Node()
            edgeS.name="e"+str(i)+"_"+str(index)
            edgeS.node=self.addSwitch(edgeS.name,cls=self.EdgeSwitchType)
            self.AllNodes.add(edgeS)
            e.append(edgeS)
            #print("adding edge switch",edgeS.name)

            server=Node()
            server.name="server"+str(i)+"_"+str(index)
            server.node=self.addHost(server.name,cls=self.HostType)
            self.AllNodes.add(server)
            #print("adding server",server.name)


            #link.setlink(self.addLink)
            self.Linking(edgeS,server)

        for i in range(len(a)):
            aggS=a[i]
            for j in range(len(e)):
                edgeS=e[j]

                #link.setlink(self.addLink)
                self.Linking(aggS,edgeS)

        return a
    #fat tree builder
    def buildTopo(self):

        self.coreswitches=[]
        self.block=[]

        #print("building net topo")


        for i in range(self.coreNum):

            coreS=Node()
            coreS.name="c"+str(i)
            coreS.node=self.addSwitch(coreS.name,cls=self.CoreSwitchType)
            self.AllNodes.add(coreS)
            self.block.append(self.createBlock(i))
            self.coreswitches.append(coreS)
            #print("adding core Switch",coreS.name)

        for i in range(len(self.coreswitches)):
            coreS=self.coreswitches[i]
            for j in range(len(self.block)):
                aggIndex=i%self.aggreagationNum
                block=self.block[j]
                aggS=block[aggIndex]

                #link.setlink(self.addLink)
                self.Linking(coreS,aggS)

        #add an outer test Node
        router=Node()
        router.name='outerReq'
        router.node = self.addHost('outerReq',cls=Host)
        self.AllNodes.add(router)
        for i in range(len(self.coreswitches)):
            coreS=self.coreswitches[i]
            self.Linking(router,coreS)

        #print("topo init finshed")


    def __init__(self):
        Topo.__init__(self)
        self.coreNum = 10
        self.aggreagationNum = 10
        self.edgeNum = 5

        self.CoreSwitchType = OVSSwitch
        self.AggregationSwitchType = OVSSwitch
        self.EdgeSwitchType = OVSSwitch
        self.HostType = Host
        self.AllNodes=set()

        self.buildTopo()
        #self.test1()

    #test topo
    def test1(self):
        c=[]
        a=[]
        e=[]
        h=[]
        for i in range(1):
            c.append(self.addSwitch('core'+str(i)))
            for j in range(2):
                a.append(self.addSwitch('agg'+str(j)+"_"+str(i)))
                self.addLink(c[i],a[len(a)-1])
                e.append(self.addSwitch('edge'+str(j)+"_"+str(i)))
                self.addLink(a[len(a)-1],e[len(e)-1])
                h.append(self.addHost('h'+str(len(h))))
                self.addLink(e[len(e)-1],h[len(h)-1])



topos={'FT':(lambda :FatTree())}




