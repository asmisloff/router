from itertools import combinations, combinations_with_replacement
from typing import Dict, List
from context import AcNetwork, ISchemaEdge, ISchemaNode
from graph import Graph
from network import Network
from prepareNodes import BranchNetworkChain, arrangeNodesByBranchIndex, buildBranchPartitions


class Router:
    """ Трассировщик """

    def __init__(self, graph: Graph, networks: Dict[int, List[AcNetwork]]) -> None:
        self.__graph = graph
        self.__network: Dict[int, BranchNetworkChain] = {
            li: BranchNetworkChain.fromAcNetwork(ntw) for li, ntw in networks.items()
        }

    def wire(self):
        """ Выполнить трассировку схемы """
        for branchIndex in self.__network.keys():
            partitions = buildBranchPartitions(
                arrangeNodesByBranchIndex(self.__graph.nodes()),
                self.__network,
                branchIndex
            )
            for ls, rs in partitions:
                for n in ls.nodes + rs.nodes:
                    self.__graph.addNode(n)
                for n1, n2 in combinations(ls.nodes + rs.nodes, 2):
                    self.__graph.addEdge(n1, n2, ISchemaEdge())
