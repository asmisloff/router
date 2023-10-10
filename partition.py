from typing import List, Set, Tuple
from cell import Cell

from context import AcNetworkLattice, ICircuitNode, ISchemaPayload
from graph import Graph
from network import NetworkSection


class Partition:
    """ Раздел ТС. """

    def __init__(
            self,
            xLeft: int,
            xRight: int,
            leftSection: NetworkSection,
            rightSection: NetworkSection,
            zeroNode: ICircuitNode,
            lattice: AcNetworkLattice,
            graph: Graph
    ) -> None:
        self.xLeft = xLeft
        self.xRight = xRight
        self.leftSection = leftSection
        self.rightSection = rightSection
        self.zeroNode: ICircuitNode = zeroNode
        self.firstCell = None
        self.lastCell = None
        self.__capacity = 1
        self.lattice = lattice
        self.graph = graph
        self.__payloads: List[ISchemaPayload] = []

    def updateCapacity(self, payloadCoordinates: List[int]):
        """ Обновить значение емкости раздела. """
        coordinates: Set[int] = set()
        for x in payloadCoordinates:
            if x > self.xLeft and x < self.xRight:
                coordinates.add(x)
        if len(coordinates) > self.__capacity:
            self.__capacity = len(coordinates) + 1

    def initCells(self) -> None:
        """ Создать ячейки в количестве, равном текущему значению емкости. """
        makeCell = lambda xl, xr, ls, rs: Cell(xl, xr, ls, rs, self.lattice, self.graph, self.zeroNode)

        if self.__capacity == 1:
            self.firstCell = makeCell(self.xLeft, self.xRight, self.leftSection, self.rightSection)
            self.lastCell = self.firstCell
            return

        self.firstCell = makeCell(self.xLeft, self.xRight, self.leftSection, self.rightSection.deepCopy())
        prev = self.firstCell
        for _ in range(self.__capacity - 1):
            next = makeCell(self.xRight, self.xRight, prev.rightSection, self.rightSection.deepCopy())
            next.prev = prev
            prev.next = next
            prev = next
        self.lastCell = makeCell(self.xRight, self.xRight, prev.rightSection, self.rightSection)

    def addPayload(self, pl: ISchemaPayload) -> bool:
        if self.firstCell is None or self.lastCell is None:
            raise Exception()
        if pl.x >= self.xLeft and pl.x <= self.xRight:
            self.__payloads.append(pl)
            return True
        return False

    def addPayloads(self, pls: List[ISchemaPayload]) -> int:
        cnt = 0
        for pl in pls:
            if self.addPayload(pl):
                cnt += 1
        return cnt

    def arrangePayloads(self) -> None:
        if self.firstCell is None or self.lastCell is None:
            raise Exception()
        self.__payloads.sort(key=lambda pl: pl.x)
        # стянуть все ячейки к правой границе
        self.firstCell.pullRightSection(self.lastCell.xRight)
        cell = self.firstCell
        for pl in self.__payloads:
            cell, n = self.__addPayloadToCell(cell, pl)
            self.graph.addEdge(n, self.zeroNode, pl.iplEdge)

    def removePayloads(self):
        self.__payloads.clear()

    def __addPayloadToCell(self, cell: Cell, pl: ISchemaPayload) -> Tuple[Cell, ICircuitNode]:
        if cell.xLeft == pl.x or cell.xRight == pl.x:
            return cell, cell.getConnectingNode(pl)
        elif pl.x < cell.xRight:
            cell.pullRightSection(pl.x)
            return cell, cell.getConnectingNode(pl)
        elif pl.x > cell.xRight and cell.next is not None:
            return self.__addPayloadToCell(cell.next, pl)
        else:
            raise Exception()

    def __repr__(self) -> str:
        return f"{{ left: {self.leftSection}, right: {self.rightSection} }}"
