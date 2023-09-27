from itertools import combinations
from context import ISchemaEdge, ISchemaNode
from graph import Graph
from network import Network


class Router:
    """ Трассировщик """
    
    def __init__(self, graph: Graph, network: Network) -> None:
        self.__graph = graph
        self.__network = network
        #Здесь должны еще быть сгруппированные по индексам ветвей списки с разделами ТС, а в разделах ячейки.
        for ranges in network.rangesByBranchIndex.values(): # узлы секций КС
            for rng in ranges:
                for tn1, tn2 in rng.rr:
                    if tn1 == tn2:
                        self.__graph.addNode(ISchemaNode(tn1, rng.xMax))


    def wire(self):
        """ Выполнить трассировку схемы """
        for branchIndex, branchNodes in self.__graph.getIterators().items():
            for left, right in branchNodes:
                # Вместо написанного дальше построить и сохранить здесь разделы ТС branchIndex-ой ветви (partitions-and-cells.ipynb).
                nodes = list(left.values()) + list(right.values())
                for n1, n2 in combinations(nodes, 2):
                    self.__graph.addNode(n1)
                    self.__graph.addNode(n2)
                    self.__graph.addEdge(ISchemaEdge(n1, n2))
