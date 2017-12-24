from SimpleNet.simplenode import *
class FatTree:


    #build block of edge and aggreagation switches
    def createBlock(self,index):
        a=[]
        e=[]
        for i in range(self.aggreagationNum):
            aggS=Node()
            aggS.name="a"+str(i)+"_"+str(index)
            self.AllNodes.add(aggS)
            a.append(aggS)
            print("adding aggregation switch",aggS.name)

        for i in range(self.edgeNum):

            edgeS=Node()
            edgeS.name="e"+str(i)+"_"+str(index)
            self.AllNodes.add(edgeS)
            e.append(edgeS)
            print("adding edge switch",edgeS.name)

            server=Server(role='Receiver')
            server.name="server"+str(i)+"_"+str(index)
            self.AllNodes.add(server)
            self.Servers.add(server)
            print("adding server",server.name)

            link=Link(edgeS,server,bw=100)
            link.setlink()
            self.AllLinks.add(link)

        for i in range(len(a)):
            aggS=a[i]
            for j in range(len(e)):
                edgeS=e[j]
                link=Link(aggS,edgeS,bw=10)
                link.setlink()
                self.AllLinks.add(link)

        return a
    #fat tree builder
    def buildTopo(self):

        self.coreswitches=[]
        self.block=[]

        #print("building net topo")


        for i in range(self.coreNum):

            coreS=Node(pf=1000,capacity=2000)
            coreS.name="c"+str(i)
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

                link=Link(coreS,aggS,bw=1000)
                link.setlink()
                self.AllLinks.add(link)

        self.statistics()



    def addOuterReqClient(self,name='OuterReq'):
        # add an outer test Node,with quite big performance and infinite capcacity
        # this node simulate request from outer clients to the data center
        router = Server(role='Sender',pf=10000, capacity=-1)
        router.name = name
        self.AllNodes.add(router)
        for i in range(len(self.coreswitches)):
            coreS = self.coreswitches[i]
            link = Link(coreS, router, bw=2000)
            link.setlink()
            self.AllLinks.add(link)
        self.outerReq.add(router)

    def statistics(self):
        servers=self.Servers
        nodes=self.AllNodes
        switches=nodes-servers-self.outerReq
        print("topo init finshed with %d links and %d nodes, and %d are servers, %d are switches, %d are outerReqClients"
              % (len(self.AllLinks), len(nodes), len(servers),len(switches),len(self.outerReq)))
    def __init__(self):
        self.coreNum = 10
        self.aggreagationNum = 8
        self.edgeNum = 5

        self.AllNodes=set()
        self.AllLinks=set()

        self.Servers=set()
        self.outerReq=set()


if __name__ == '__main__':
    ft=FatTree()
    ft.buildTopo()
    ft.addOuterReqClient('outerR1')
    ft.addOuterReqClient('outerR2')
    ft.statistics()
