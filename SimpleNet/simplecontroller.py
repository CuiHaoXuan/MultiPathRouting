#def net controller
from simplenode import *
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

    def SetFlowRule(self,route,id):
        #route is a list descibe routing from src to dst
        #index asc from src to dst
        for i in range(len(route)-1):
            node=route[i]
            fr = FlowRule()
            fr.dataID = id
            fr.nextNode = route[i+1]
            curNode=self.getNodeByName(node)
            for rule in curNode.ForwardingTable:
                if rule.id==id:
                    curNode.ForwardingTable.remove(rule)
                    break
            curNode.ForwardingTable=set()
            curNode.ForwardingTable.add(fr)

    def getNodeByName(self,name):
        nodes=self.Topo.AllNodes
        for node in nodes:
            if node.name==name:
                return node
        return None
    def generatePktID(self):
        id=''

        return id