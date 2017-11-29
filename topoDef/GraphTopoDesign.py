#graph topology design

class node:
    neighbor=[]
    name=''
    def __init__(self,name):
        self.name=name
class Graph:
    linkCount=0

    def addneighbor2(self,node1,node2):
        node1.neighbor.append(node2)
        node2.neighbor.append(node1)
        self.linkCount=self.linkCount+1
class FatTree(Graph):
    c=[]#core switch
    a=[]#aggregation switch
    s=[]#edge switch
    h=[]#host
    '''make sure that nc%na==0'''
    nc = 6  # total core switch
    na = 3  # aggregation switch in one block
    ns = 2  # edge switch in one block
    nh = 2  # host connected to each edge switch
    midblock={}#middle block area

    def addblock(self,anodes,snodes):
        for a in anodes:
            for s in snodes:
                self.addneighbor2(a,s)

    def createBlock(self,index):
        a=[]
        s=[]
        h=[]
        m=self.na
        n=self.ns

        for i in xrange(m):
            a.append(node('aggregation_'+str(index+1)+'_'+str(i+1)))
        for i in xrange(n):
            s.append(node('edge_'+str(index+1)+'_'+str(i+1)))
            for j in xrange(self.nh):
                h.append(node('host_'+str(index+1)+'_'+str(i+1)+'_'+str(j+1)))
                self.addneighbor2(s[i],h[j])


        self.addblock(a,s)
        self.midblock[index]=a
        self.a=self.a+a
        self.s=self.s+s
        self.h=self.h+h

    def generateTopo(self):

        c=[]

        for i in xrange(self.nc):
            c.append(node('core'+str(i+1)))
            self.createBlock(i)
        for i in xrange(self.nc):
            k=self.nc%self.na
            for j in xrange(self.nc):
                self.addneighbor2(c[j],self.midblock[i][k])
                pass
        self.c=self.c+c

#test
if __name__=="__main__":
    ftree=FatTree()
    ftree.generateTopo()
    print "FatTree,linkCount=",ftree.linkCount
    #exit(0)
    for c in ftree.c:
        print c.name
    for a in ftree.a:
        print a.name
    for s in ftree.s:
        print s.name
    for h in ftree.h:
        print h.name
