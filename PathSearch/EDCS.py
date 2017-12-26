from BFS import *
#dynamic measure cost of each node
def compare_list(node1,node2):
    if node1.cost>node2.cost:
        return 1
    elif node1.cost<node2.cost:
        return -1
    else:
        return 0

#mergeSort
def merge(left,right):
    A=[]
    j=0
    i=0
    while i<len(left) and j<len(right):
        if compare_list(left[i],right[j])>=0: # left[i]>=right[j]:
            A.append(left[i])
            i=i+1
        else:
            A.append(right[j])
            j=j+1
    if len(left)>i:
        A=A+left[i:]
    if len(right)>j:
        A=A+right[j:]
    return A

def mergeSort(A):
    #A is a sequence
    if len(A)<2:
        return A

    seg=1
    while seg<len(A):
        i=0
        while i<len(A)-seg:
            left=A[i:i+seg]
            right=A[i+seg:i+2*seg]
            #print("L",left)
            #print("R",right)
            A[i:i+2*seg]=merge(left,right)
            i=i+2*seg
        seg=seg*2

    return A


def SortAdd(table,node):
    #asc by cost of node
    table.append(node)
    table=mergeSort(table)
    return table
def EDCS(sN,tN,graph):
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
                #openT.append(nextnode)
                nextnode.cost=curNode.cost+nextnode.cachaeSize()+2.0
                openT=SortAdd(openT,nextnode)
                #print 'add', nextnode.name


    if tag==False:
        print("not connected? Inner Error")
        exit(1)
    #print 'path from',nodeP.name
    curNode=nodeP
    route=[]
    route.insert(0,curNode.name)
    while curNode.prevNode is not None:
        #print curNode.name
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
    sN=startNode
    tN=targetNode
    route=EDCS(sN,tN,graph)
    for node in route:
        print(node)
