from typing import List, Set, Tuple
from cell import Cell

from context import AcNetworkLattice, ISchemaNode, ISchemaPayload
from graph import Graph
from network import NetworkSection


class Partition:
    def __init__(
            self,
            xLeft: int,
            xRight: int,
            leftSection: NetworkSection,
            rightSection: NetworkSection,
            zeroNode: ISchemaNode,
            lattice: AcNetworkLattice,
            graph: Graph
    ) -> None:
        self.xLeft = xLeft
        self.xRight = xRight
        self.leftSection = leftSection
        self.rightSection = rightSection
        self.zeroNode: ISchemaNode = zeroNode
        self.firstCell = None
        self.lastCell = None
        self.__payloads: List[ISchemaPayload] = []
        self.__cellQty = 1
        self.lattice = lattice
        self.graph = graph

    def ensureCapacity(self, payloadCoordinates: List[int]):
        coordinates: Set[int] = set()
        for x in payloadCoordinates:
            if x > self.xLeft and x < self.xRight:
                coordinates.add(x)
        if len(coordinates) > self.__cellQty:
            self.__cellQty = len(coordinates) + 1

    def initCells(self) -> None:
        rightSection = NetworkSection()
        rightSection.nodes = [
            ISchemaNode.createInstance(self.xRight, n.branchIndex(), n.relativeLineIndex()) for n in self.rightSection
        ]
        self.firstCell = Cell(self.xLeft, self.xRight, self.leftSection, rightSection, self.lattice)
        prev = self.firstCell
        for _ in range(1, self.__cellQty):
            rightSection = NetworkSection()
            rightSection.nodes = [
                ISchemaNode.createInstance(self.xRight, n.branchIndex(), n.relativeLineIndex()) for n in self.rightSection
            ]
            next = Cell(self.xRight, self.xRight, prev.rightSection, rightSection, self.lattice)
            next.prev = prev
            prev.next = next
            prev = next
        self.lastCell = prev
        self.lastCell.rightSection = self.rightSection
        cell = self.firstCell
        while cell is not None:
            cell.mergeInto(self.graph, self.zeroNode)
            cell = cell.next

    def addPayload(self, pl: ISchemaPayload) -> bool:
        if self.firstCell is None or self.lastCell is None:
            raise Exception()
        if pl.x > self.xLeft and pl.x < self.xRight:
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

    def __addPayloadToCell(self, cell: Cell, pl: ISchemaPayload) -> Tuple[Cell, ISchemaNode]:
        if cell.xLeft == pl.x or cell.xRight == pl.x:
            return cell, cell.findNodeToConnect(pl)
        elif pl.x < cell.xRight:
            cell.pullRightSection(pl.x)
            return cell, cell.findNodeToConnect(pl)
        elif pl.x > cell.xRight and cell.next is not None:
            return self.__addPayloadToCell(cell.next, pl)
        else:
            raise Exception()
    
    def __repr__(self) -> str:
        return f"{{ left: {self.leftSection}, right: {self.rightSection} }}"
