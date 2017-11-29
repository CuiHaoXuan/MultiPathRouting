"""
Data Center topology example

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology.Enables each one to pass in '--topo=<key>' from the command line.
"""

from mininet.topo import Topo


class BCubeTopo(Topo):
    """
    This topology is defined as a recursive structure. A :math:`Bcube_0` is 
    composed of n hosts connected to an n-port switch. A :math:`Bcube_1` is 
    composed of n :math:`Bcube_0` connected to n n-port switches. A :math:`Bcube_k` is
    composed of n :math:`Bcube_{k-1}` connected to :math:`n^k` n-port switches.

    This topology comprises:
     * :math:`n^(k+1)` hosts, each of them connected to :math:`k+1` switches
     * :math:`n*(k+1)` switches, each of them having n ports

    Parameters
    ----------
    k : int
        The level of Bcube
    n : int
        The number of host per :math:`Bcube_0`
    """

    def __init__(self, k=1, n=4):
        "Create bcube topo."

        # Initialize topology
        Topo.__init__(self)

        # Validate input arguments
        if not isinstance(n, int) or not isinstance(k, int):
            raise TypeError('k and n arguments must be of int type')
        if n < 1:
            raise ValueError("Invalid n parameter. It should be >= 1")
        if k < 0:
            raise ValueError("Invalid k parameter. It should be >= 0")

        # add hosts
        n_hosts = n ** (k + 1)
        for i in xrange(n_hosts):
            self.addHost('h{}_{}'.format(i / n, i % n))

        # add switches according level and connect with hosts
        for level in xrange(k + 1):
            sid = 0
            arg1 = n ** level
            arg2 = n ** (level + 1)
            # i is the horizontal position of a switch a specific level
            for i in xrange(n ** k):
                # add switch at given level
                sw = self.addSwitch('s{}_{}'.format(level, sid))
                # add links between hosts and switch
                m = i % arg1 + i / arg1 * arg2
                hosts = xrange(m, m + arg2, arg1)
                nodeslist = self.nodes()
                sid = sid + 1
                for v in hosts:
                    self.addLink(sw, nodeslist[v])


class FatTreeTopo(Topo):
    """
    A fat tree topology built using k-port switches can support up to
    :math:`(k^3)/4` hosts. This topology comprises k pods with two layers of
    :math:`k/2` switches each. In each pod, each aggregation switch is
    connected to all the :math:`k/2` edge switches and each edge switch is
    connected to :math:`k/2` hosts. There are :math:`(k/2)^2` core switches,
    each of them connected to one aggregation switch per pod.As for the
    blocking Fat-Tree network, we vary its oversubscription ratio by cutting
    the number of core switches. In a blocking Fat-Tree with r:1 oversubscription
    ratio, the number of core switches is 1/r of that in the original Fat-Tree.

    Parameters
    ----------
    k : int
        The number of ports of the switches
    r : int
        The oversubscription ratio of blocking Fat-Tree
    """

    def __init__(self, k=2, r=1):
        "Create fat_tree topo."

        c = []  # core
        a = []  # aggravate
        e = []  # edge
        s = []  # switch

        # Initialize topology
        Topo.__init__(self)

        # validate input arguments
        if not isinstance(k, int):
            raise TypeError('k argument must be of int type')
        if not isinstance(r, int):
            raise TypeError('r argument must be of int type')
        if k // 2 % r != 0:
            raise ValueError('k/2 must be divided exactly by r')
        if k < 1 or k % 2 == 1:
            raise ValueError('k must be a positive even integer')

        # Create core nodes
        n_core = ((k // 2) ** 2) // r
        for i in xrange(n_core):
            sw = self.addSwitch('c{}'.format(i + 1))
            c.append(sw)
            s.append(sw)

        # Create aggregation and edge nodes and connect them
        for pod in xrange(k):
            aggr_start_node = len(s) + 1
            aggr_end_node = aggr_start_node + k // 2
            edge_start_node = aggr_end_node
            edge_end_node = edge_start_node + k // 2
            aggr_nodes = xrange(aggr_start_node, aggr_end_node)
            edge_nodes = xrange(edge_start_node, edge_end_node)
            for i in aggr_nodes:
                sw = self.addSwitch('a{}'.format(i))
                a.append(sw)
                s.append(sw)
            for j in edge_nodes:
                sw = self.addSwitch('e{}'.format(j))
                e.append(sw)
                s.append(sw)
            for aa in aggr_nodes:
                for ee in edge_nodes:
                    self.addLink(s[aa - 1], s[ee - 1])

        # Connect core switches to aggregation switches
        for core_node in xrange(n_core):
            for pod in xrange(k):
                aggr_node = n_core + (core_node // ((k // 2) // r)) + (k * pod)
                self.addLink(s[core_node], s[aggr_node])

        # Create hosts and connect them to edge switches
        count = 1
        for sw in e:
            for i in xrange(k / 2):
                host = self.addHost('h{}'.format(count))
                self.addLink(sw, host)
                count += 1


topos = {'bcube': BCubeTopo, 'fattree': FatTreeTopo}
