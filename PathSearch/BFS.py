from topoDef.MininetFatTreeTopo import *
import threading
def matchNodeInGraph(node1,node2,graph):
    Nlist=graph.AllNodes
    nodeS=None
    nodeP=None
    tag=[False,False]
    for node in Nlist:
        if False==tag[0] and node.getName()==node1.getName():
            nodeS=node
            tag[0]=True
        if False==tag[1] and node.getName()==node2.getName():
            nodeP=node
            tag[1]=True
    if False in tag:
        print tag
        exit(2)
    print len(nodeS.getNeighbors()),len(nodeP.getNeighbors())
    return [nodeS,nodeP]
def BFS(sN,tN,graph):
    ftree = graph

    nodeS,nodeP=matchNodeInGraph(sN,tN,ftree)

    openT=[]
    closeT=[]
    openT.append(nodeS)
    tag=False
    count=1
    while len(openT)>0 and tag==False:

        closeT.append(openT[0])
        curNode=openT[0]
        openT.pop(0)
        print curNode.getName(),'neighbor=',len(curNode.getNeighbors())
        #threading._sleep(1)
        for nextnode in curNode.getNeighbors():

            if nextnode.getName() == nodeP.getName():
                curNode.connectNode(nextnode)
                print "found", nodeP.getName(),nextnode.getName()
                tag=True
                break

            if nextnode not in closeT and nextnode not in openT:
                curNode.connectNode(nextnode)
                openT.append(nextnode)
                print 'add', nextnode.getName()


    if tag==False:
        exit(1)
    print 'path from',nodeP.getName()
    curNode=nodeP

    while curNode.prevNode is not None:
        print curNode.getName()
        curNode=curNode.prevNode
    print curNode.getName()


if __name__=="__main__":
    graph=FatTree()
    startNode=raw_input("start node:")
    targetNode=raw_input("target node:")
    print "from",startNode,'to',targetNode
    sN=Node()
    tN=Node()
    sN.name=startNode
    tN.name=targetNode
    BFS(sN,tN,graph)

