from SimpleNet.topo_fattree import *

def matchNodeInGraph(node1,node2,graph):
    Nlist=graph.AllNodes
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
        #print curNode.name,'neighbor=',len(curNode.getNeighbors())
        #threading._sleep(1)
        for nextnode in curNode.getNeighbors():

            if nextnode.name == nodeP.name:
                curNode.connectNode(nextnode)
                print "found", nodeP.name,nextnode.name
                tag=True
                break

            if nextnode not in closeT and nextnode not in openT:
                curNode.connectNode(nextnode)
                openT.append(nextnode)
                #print 'add', nextnode.name


    if tag==False:
        print("not connected? Inner Error")
        exit(1)
    print 'path from',nodeP.name
    curNode=nodeP
    route=[]
    route.insert(0,curNode.name)
    while curNode.prevNode is not None:
        print curNode.name
        curNode=curNode.prevNode
        route.insert(0,curNode.name)
    print curNode.name

    return route

if __name__=="__main__":
    graph=FatTree()
    graph.buildTopo()
    graph.addOuterReqClient('outer1')
    graph.addOuterReqClient('outer2')

    startNode=raw_input("start node:")
    targetNode=raw_input("target node:")
    print "from",startNode,'to',targetNode
    sN=Node()
    tN=Node()
    sN.name=startNode
    tN.name=targetNode
    route=BFS(sN,tN,graph)
    for node in route:
        print(node)

