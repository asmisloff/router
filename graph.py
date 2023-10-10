from typing import Iterable, Set
from matplotlib import pyplot as plt
from context import ICircuitEdge, ICircuitNode


class Graph:
    """ Имитирует граф схемы """

    def __init__(self, nodes: Iterable[ICircuitNode]) -> None:
        self.__nodes: Set[ICircuitNode] = set()
        self.__edges: Set[ICircuitEdge] = set()
        self.__nodesBeforeWiring: Set[ICircuitNode] = set()
        for n in nodes:
            self.addNode(n)
            self.__nodesBeforeWiring.add(n)

    def nodes(self) -> Set[ICircuitNode]:
        return self.__nodes

    def addNode(self, node: ICircuitNode) -> None:
        """ Добавить узел """
        self.__nodes.add(node)

    def addEdge(self, src: ICircuitNode, tgt: ICircuitNode, edge: ICircuitEdge) -> None:
        """ Добавить ребро """
        edge._ICircuitEdge__source = src  # type: ignore
        edge._ICircuitEdge__target = tgt  # type: ignore
        self.__edges.add(edge)

    def plot(self, showZeroNode: bool = False, shift: float = 0.25) -> None:
        """ Разместить узлы и ребра на графике """
        f, (ax1, ax2) = plt.subplots(2)

        xxSrc = []
        yySrc = []
        ccSrc = []
        for n in self.__nodesBeforeWiring:
            c = "red" if n.breaking else "black"
            ccSrc.append(c)
            xxSrc.append(n.axisCoordinate())
            yySrc.append(-n.lineIndex)
        ax1.scatter(xxSrc, yySrc, c=ccSrc, s=5)

        xx = []
        yy = []
        cc = []
        for n in self.__nodes:
            if not showZeroNode and n.relativeLineIndex() == 0:
                continue
            x = n.axisCoordinate() if not n.duplicatedBreakingNode else n.axisCoordinate() + shift
            xx.append(x)
            yy.append(-n.lineIndex)
            c = "blue"
            if n in self.__nodesBeforeWiring:
                c = "black"
            if n.breaking:
                c = "red"
            cc.append(c)

        edges = []
        for e in self.__edges:
            if not showZeroNode and e.getTargetNode().relativeLineIndex() == 0:
                continue
            n1 = e.getSourceNode()
            x1 = n1.axisCoordinate() if not n1.duplicatedBreakingNode else n1.axisCoordinate() + shift
            n2 = e.getTargetNode()
            x2 = n2.axisCoordinate() if not n2.duplicatedBreakingNode else n2.axisCoordinate() + shift
            edges.append([x1, x2])
            edges.append([-n1.lineIndex, -n2.lineIndex])

        ax2.scatter(xx, yy, c=cc, s=5)
        ax2.plot(*edges, c="black", linewidth=0.2)
        ax1.set_title("До трассировки")
        ax2.set_title("После")
        for ax in (ax1, ax2):
            ax.set_yticks([-1, -2, -3], labels=["1-я линия", "2-я линия", "3-я линия"])
        f.tight_layout()
        plt.show()
