from itertools import combinations_with_replacement
from typing import List, Set

from context import AcNetworkLattice, ISchemaEdge, ISchemaNode, ISchemaPayload, Side
from graph import Graph
from network import NetworkSection
    

class Cell:
    """ Ячейка ТС. """

    def __init__(
            self,
            xLeft: int,
            xRight: int,
            leftSection: NetworkSection,
            rightSection: NetworkSection,
            lattice: AcNetworkLattice,
            graph: Graph,
            zeroNode: ISchemaNode
    ):
        self.next: "Cell" | None = None
        self.prev: "Cell" | None = None
        self.xLeft: int = xLeft
        self.xRight: int = xRight
        self.leftSection = leftSection
        self.rightSection = rightSection
        self.lattice = lattice
        self.edges: Set[ISchemaEdge] = set()
        self.__mergeInto(graph, zeroNode)
    
    def __mergeInto(self, graph: Graph, zeroNode: ISchemaNode):
        # Рассмотреть все сочетания узлов из n по 2, для каждой пары создать ребро и добавить его в граф схемы.
        graph.addNode(zeroNode)
        for n in self.leftSection.nodes + self.rightSection.nodes:
            graph.addNode(n)
        for i, j in combinations_with_replacement(range(self.leftSection.size() + self.rightSection.size()), 2):
            # Это не тестировалось, может работать неправильно.
            n1: ISchemaNode
            n2: ISchemaNode
            side1: Side
            side2: Side
            li1: int
            li2: int
            if i < self.leftSection.size():
                n1 = self.leftSection.get(i)
                side1 = Side.Left
            else:
                n1 = self.rightSection.get(i - self.leftSection.size())
                side1 = Side.Right
            li1 = n1.relativeLineIndex()
            if j < self.leftSection.size():
                n2 = self.leftSection.get(j)
                side2 = Side.Left
            else:
                n2 = self.rightSection.get(j - self.leftSection.size())
                side2 = Side.Right
            li2 = n2.relativeLineIndex()
            e = ISchemaEdge.createWithCond(self.lattice.cond(li1, side1, li2, side2, self.xRight - self.xLeft))
            graph.addEdge(n1, n2 if n2 != n1 else zeroNode, e)
            self.edges.add(e)

    def pullRightSection(self, destPoint: int) -> None:
        """ Притянуть ячейку за правое сечение в заданную точку. """
        if not destPoint == self.xRight:
            destPoint = round(destPoint, 3)
            self.xRight = destPoint
            for n in self.rightSection:
                n.x = destPoint
            if destPoint < self.xLeft:
                self.xLeft = destPoint
                for n in self.leftSection:
                    n.x = destPoint
                if self.prev is not None:
                    self.prev.pullRightSection(destPoint)
            self.__updateEdgeConductivities()
            if self.next is not None:
                self.next.pullLeftSection(destPoint)

    def pullLeftSection(self, destPoint: int) -> None:
        """ Притянуть ячейку за левое сечение в заданную точку. """
        if not destPoint == self.xLeft:
            destPoint = round(destPoint, 3)
            self.xLeft = destPoint
            for n in self.leftSection:
                n.x = destPoint
            if destPoint > self.xRight:
                self.xRight = destPoint
                for n in self.rightSection:
                    n.x = destPoint
                if self.next is not None:
                    self.next.pullLeftSection(destPoint)
            self.__updateEdgeConductivities()
            if self.prev is not None:
                self.prev.pullRightSection(destPoint)
    
    def findNodeToConnect(self, pl: ISchemaPayload) -> ISchemaNode:
        for lst in self.leftSection, self.rightSection:
            for n in lst:
                if n.x == pl.x and pl.trackNumber == n.lineIndex:
                    return n
        raise Exception("Не найден узел для подключения нагрузки")
    
    def __updateEdgeConductivities(self):
        length = self.xRight - self.xLeft
        for e in self.edges:
            n1 = e.getSourceNode()
            n2 = e.getTargetNode()
            side1 = Side.Left if n1 in self.leftSection else Side.Right
            side2 = Side.Left if n2 in self.leftSection else Side.Right
            if n2.lineIndex % 10_000 == 0:
                e.c = self.lattice.cond(n1.lineIndex, side1, n1.lineIndex, side1, length)
            elif n1.lineIndex % 10_000 == 0:
                e.c = self.lattice.cond(n2.lineIndex, side2, n2.lineIndex, side2, length)
            e.c = self.lattice.cond(n1.lineIndex, side1, n2.lineIndex, side2, length)

    def __repr__(self) -> str:
        return f"{{left: {{x: {self.xLeft}, section: {self.leftSection}}}, right: {{x: {self.xRight}, section: {self.rightSection}}}}}"