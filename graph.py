from typing import Iterable, List, Set
from matplotlib import pyplot as plt
from context import ISchemaEdge, ISchemaNode


class Graph:
    """ Имитирует граф схемы """

    def __init__(self, nodes: Iterable[ISchemaNode]) -> None:
        self.__nodes: Set[ISchemaNode] = set()
        self.__edges: Set[ISchemaEdge] = set()
        self.__nodesBeforeWiring: Set[ISchemaNode] = set()
        for n in nodes:
            self.addNode(n)
            self.__nodesBeforeWiring.add(n)
    
    def nodes(self) -> Set[ISchemaNode]:
        return self.__nodes

    def addNode(self, node: ISchemaNode) -> None:
        """ Добавить узел """
        self.__nodes.add(node)

    def addEdge(self, src: ISchemaNode, tgt: ISchemaNode, edge: ISchemaEdge) -> None:
        """ Добавить ребро """
        edge._ISchemaEdge__source = src # type: ignore
        edge._ISchemaEdge__target = tgt # type: ignore
        self.__edges.add(edge)

    def plot(self, shift: float = 0.25) -> None:
        """ Разместить узлы и ребра на графике """
        f, (ax1, ax2) = plt.subplots(2)

        xxSrc = []
        yySrc = []
        ccSrc = []
        for n in self.__nodesBeforeWiring:
            c = "red" if n.breaking else "black"
            ccSrc.append(c)
            xxSrc.append(n.axisCoordinate())
            yySrc.append(n.lineIndex)
        ax1.scatter(xxSrc, yySrc, c=ccSrc, s=5)

        xx = []
        yy = []
        cc = []
        edges = []
        connectedNodes: Set[ISchemaNode] = set()
        for e in self.__edges:
            for n in (e.getSourceNode(), e.getTargetNode()):
                if n not in connectedNodes and n.duplicatedBreakingNode:
                    n.x += round(shift * 1000)
            connectedNodes.add(e.getSourceNode())
            connectedNodes.add(e.getTargetNode())
            edges.append([e.getSourceNode().axisCoordinate(), e.getTargetNode().axisCoordinate()])
            edges.append([e.getSourceNode().lineIndex, e.getTargetNode().lineIndex])
        for n in connectedNodes:
            c = "blue"
            if n in self.__nodesBeforeWiring:
                c = "black"
            if n.breaking:
                c = "red"
            cc.append(c)
            xx.append(n.axisCoordinate())
            yy.append(n.lineIndex)
        ax2.scatter(xx, yy, c=cc, s=5)
        ax2.plot(*edges, c="black", linewidth=0.2)
        ax1.set_title("До трассировки")
        ax2.set_title("После")
        f.tight_layout()
        plt.show()
