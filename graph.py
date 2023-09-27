from collections import deque
from typing import Deque, Dict, List, Set
from matplotlib import pyplot as plt
from iterator import SectionNodeIterator
from context import ISchemaEdge, ISchemaNode
from network import Network


class Graph:
    """ Имитирует граф схемы """

    def __init__(self, nodes: List[ISchemaNode]) -> None:
        self.__nodes: Set[ISchemaNode] = set()
        self.__edges: Set[ISchemaEdge] = set()
        self.__nodesBeforeWiring: Set[ISchemaNode] = set()
        for n in nodes:
            self.addNode(n)
            self.__nodesBeforeWiring.add(n)

    def addNode(self, node: ISchemaNode) -> None:
        """ Добавить узел """
        self.__nodes.add(node)

    def addEdge(self, edge: ISchemaEdge) -> None:
        """ Добавить ребро """
        self.__edges.add(edge)

    def getIterators(self) -> Dict[int, SectionNodeIterator]:
        """ Создает и возвращает итераторы по сечениям. { branchIndex: iterator } """
        nodesByBranchIndex: Dict[int, Dict[int, Deque[ISchemaNode]]] = {} #{ branchIndex: { lineIndex: queue } }
        for node in sorted(self.__nodes, key=lambda n: n.axisCoordinate):
            lineIndex = node.trackNumber
            if lineIndex > 0: #0 - земля, отрицательные индексы у внутренних узлов блоков. Они не участвуют.
                branchIndex = lineIndex // 10_000
                branchNodes = nodesByBranchIndex.get(branchIndex)
                if branchNodes is None:
                    branchNodes = {}
                    nodesByBranchIndex[branchIndex] = branchNodes
                queue = branchNodes.get(lineIndex)
                if queue is None:
                    queue = deque()
                    branchNodes[lineIndex] = queue
                queue.append(node)
        result: Dict[int, SectionNodeIterator] = {}
        for branchIndex, branchNodes in nodesByBranchIndex.items():
            result[branchIndex] = SectionNodeIterator(branchNodes)
        print(result)
        return result

    def plot(self, shift: float = 0.25) -> None:
        """ Разместить узлы и ребра на графике """
        f, (ax1, ax2) = plt.subplots(2)

        xxSrc = []
        yySrc = []
        ccSrc = []
        for n in self.__nodesBeforeWiring:
            c = "red" if n.breaking else "black"
            ccSrc.append(c)
            xxSrc.append(n.axisCoordinate)
            yySrc.append(n.trackNumber)
        ax1.scatter(xxSrc, yySrc, c=ccSrc, s=5)

        xx = []
        yy = []
        cc = []
        edges = []
        connectedNodes: Set[ISchemaNode] = set()
        for e in self.__edges:
            for n in (e.source, e.target):
                if n not in connectedNodes and n.duplicatedBreakingNode:
                    n.axisCoordinate += shift
            connectedNodes.add(e.source)
            connectedNodes.add(e.target)
            edges.append([e.source.axisCoordinate, e.target.axisCoordinate])
            edges.append([e.source.trackNumber, e.target.trackNumber])
        for n in connectedNodes:
            c = "blue"
            if n in self.__nodesBeforeWiring:
                c = "black"
            if n.breaking:
                c = "red"
            cc.append(c)
            xx.append(n.axisCoordinate)
            yy.append(n.trackNumber)
        ax2.scatter(xx, yy, c=cc, s=5)
        ax2.plot(*edges, c="black", linewidth=0.2)
        ax1.set_title("До трассировки")
        ax2.set_title("После")
        f.tight_layout()
        plt.show()
