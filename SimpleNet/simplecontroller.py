#def net controller
import random
import string
from simplenode import *
from topo_fattree import *
from PathSearch.BFS import *

class Controller:
    def __init__(self,topo):
        self.Topo=topo
        self.route={}

        for server in self.Topo.Servers:
            server.controller=self
        for outer in self.Topo.outerReq:
            outer.controller=self

    def begin(self):
        nodes=self.Topo.AllNodes-self.Topo.outerReq

        for node in nodes:
            node.start()

    def SearchRoute(self,sN,tN):
        route=BFS(sN,tN,self.Topo)
        print("path from",sN,"to",tN)
        for i in range(len(route)):
            print(route[i])
        return route

    def SetFlowRule(self,route,id):
        #route is a list descibe routing from src to dst
        #index asc from src to dst
        for i in range(len(route)-1):
            node=route[i]
            fr = FlowRule()
            fr.dataID = id
            fr.nextNode = route[i+1]
            curNode=self.getNodeByName(node)
            rm=None
            for rule in curNode.ForwardingTable:
                if rule.dataID==id:
                    rm=rule
                    break
            if rm is not None:
                curNode.ForwardingTable.remove(rm)
            curNode.ForwardingTable.add(fr)
            print("set node,next ===>",node,fr.nextNode)
        print("flow rule configure finished")
    def getNodeByName(self,name):
        nodes=self.Topo.AllNodes
        for node in nodes:
            if node.name==name:
                return node
        print("not found", name,"Inner Error")
        return None
    def generatePktID(self,src,dst):

        ID = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        print "generated ID=",ID

        if ID not in self.route.keys():

            self.route[ID]=self.SearchRoute(src,dst)
        return ID
    def releasePktID(self,id_pkt):
        rm=None
        for id in self.route.keys():
            if id==id_pkt:
                rm=id
                #print("removed",id)
                break
        self.route.pop(rm)

if __name__ == '__main__':

    ft = FatTree()
    ft.buildTopo()
    ft.addOuterReqClient('outerR1')
    ft.addOuterReqClient('outerR2')
    ft.statistics()
    ctr=Controller(ft)
    '''
    for i in xrange(10):
        ctr.generatePktID()
    print(len(ctr.ID_pool))
    id=None
    for i in ctr.ID_pool:
        id=i
    ctr.releasePktID(id)
    print(len(ctr.ID_pool))
    '''

    startNode = raw_input("start node:")
    targetNode = raw_input("target node:")
    sN=ctr.getNodeByName(startNode)
    tN=ctr.getNodeByName(targetNode)

    sN.prepareData(pktsize=20,totalsize=200,dst=tN.name)

    for id in ctr.route.keys():
        ctr.SetFlowRule(ctr.route[id],id)
    ctr.begin()
    sN.start()
    outers=['zzy','liu','yu','wen','dotty']
    servers=['server0_0','server3_9','server2_5','server3_8','server1_7']
    for i in range(5):
        print("==========================================")
        com.acquire()
        outerR= outers[i]
        outerR=ctr.Topo.addOuterReqClient(outerR)
        outerR.controller=ctr

        server=ctr.getNodeByName(servers[i])
        outerR.prepareData(pktsize=5,totalsize=100,dst=server.name)


        for id in ctr.route.keys():
            ctr.SetFlowRule(ctr.route[id],id)


        outerR.start()
        com.release()
        time.sleep(random.randint(0,3))




