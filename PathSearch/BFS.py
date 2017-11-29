from topoDef.GraphTopoDesign import *
import threading
def matchNodeInGraph(node1,node2,graph):
    Nlist=graph.c+graph.a+graph.s+graph.h
    nodeS=None
    nodeP=None
    tag=[False,False]
    for node in Nlist:
        if False==tag[0] and node.name==node1.name:
            nodeS=node
            tag[0]=True
        if False==tag[1] and node.name==node2.name:
            nodeP=node
            tag[1]=True
    if False in tag:
        print tag
        exit(2)
    return [node1,node2]
def BFS(nodeS,nodeP):
    ftree = FatTree()
    ftree.generateTopo()
    nodeS,nodeP=matchNodeInGraph(nodeS,nodeP,ftree)

    openT=[]
    closeT=[]
    openT.append(nodeS)

    count=1
    while len(openT)>0 and count<2:
        count=count+1
        closeT.append(openT[0])
        curNode=openT[0]
        del openT[0]
        print curNode.name,'neighbor=',len(curNode.neighbor)
        threading._sleep(10)
        for nextnode in curNode.neighbor:
            count=count+1
            if count>20:
                break
            if nextnode not in closeT and nextnode not in openT:
                curNode.connectNode(nextnode)
                openT.append(nextnode)
                print 'add', nextnode.name
            if nextnode.name == nodeP.name:
                print "found", nodeP.name,nextnode.name
                break

    curNode=nodeS
    while curNode.nextNode is not None:
        print curNode.name

if __name__=="__main__":
    startNode=raw_input("start node:")
    targetNode=raw_input("target node:")
    print "from",startNode,'to',targetNode
    BFS(node(startNode),node(targetNode))
