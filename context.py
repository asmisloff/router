from enum import Enum
from functools import total_ordering
from typing import Dict, Tuple


MutualResistivities = Dict[Tuple[int, int], complex]


class Side(Enum):
    Left = 0
    Right = 1


class AcNetworkLattice:
    def cond(self, lineIndex1: int, side1: Side, lineIndex2: int, side2: Side, length: float) -> complex:
        return 1 + 0j


@total_ordering
class ICircuitNode:
    """ 
    Похожий интерфейс используется в проекте. Нужно изменить следующее.
        - Все комплексные числа хранить в примитивных float-ов. Существующие интерфейсы поддержать через свойства.
        - Координату хранить как целое 4-байтовое число со знаком. Единица измерения - м.
        - equal и hashCode остаются как есть сейчас в проекте, отсюда не переносим.
    """

    def __init__(self, lineIndex: int, axisCoordinate: float, breaking=False) -> None:
        self.breaking = breaking
        self.lineIndex = lineIndex
        self.x = round(axisCoordinate * 1000)
        self.duplicatedBreakingNode = False

    @classmethod
    def createInstance(cls, x: int, branchIndex: int, lineIndex: int) -> "ICircuitNode":
        return ICircuitNode(branchIndex * 10_000 + lineIndex, 1e-3 * x)

    def branchIndex(self) -> int:
        return self.lineIndex // 10_000

    def relativeLineIndex(self) -> int:
        return self.lineIndex % 10_000

    def axisCoordinate(self) -> float:
        return round(self.x / 1000, 3)

    def __repr__(self) -> str:
        if self.breaking:
            return f"!{self.x}"
        if self.duplicatedBreakingNode:
            return f"~{self.x}"
        return str(self.x)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ICircuitNode):
            return False
        if self.relativeLineIndex() == 0:
            return __value.relativeLineIndex() == 0
        return id(self) == id(__value) #(self.lineIndex == __value.lineIndex) and (self.x == __value.x) and (self.breaking == __value.breaking) and (self.duplicatedBreakingNode == __value.duplicatedBreakingNode)

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, ICircuitNode):
            raise TypeError()
        return self.x < __value.x

    def __hash__(self):
        if self.relativeLineIndex() == 0:
            return 0
        return id(self)


class ICircuitEdge:
    """ Похожий интерфейс используется в проекте. Изменить способ хранения комплексных величин. """

    def __init__(self, resistance: complex = 1+0j) -> None:
        self.__source: ICircuitNode | None = None
        self.__target: ICircuitNode | None = None
        self.c = 1 / resistance

    @classmethod
    def createWithCond(cls, c: complex) -> "ICircuitEdge":
        return ICircuitEdge(1 / c)

    def setConductivity(self, conductivity: float):
        self.c = conductivity

    def getSourceNode(self) -> ICircuitNode:
        if (self.__source is None):
            raise Exception("Ребро не было добавлено в граф")
        return self.__source

    def getTargetNode(self) -> ICircuitNode:
        if (self.__target is None):
            raise Exception("Ребро не было добавлено в граф")
        return self.__target

    def __repr__(self) -> str:
        return f"{self.__source} -> {self.__target}"


class ISchemaPayload:
    def __init__(self, x: float) -> None:
        self.x: int = round(x * 1000)
        self.trackNumber: int = 1
        self.iplEdge: ICircuitEdge = ICircuitEdge()

    def __repr__(self) -> str:
        return f"{{x: {self.x}, li: {self.trackNumber % 10_000}, br: {self.trackNumber // 10_000}}}"


class AcNetworkDto:
    def __init__(self, coordinate: float, trackQty: int = 2) -> None:
        self.coordinate = round(coordinate, 3)
        self.trackQty = trackQty

    def __repr__(self) -> str:
        return f"{{ xRight: {self.coordinate}, trackQty: {self.trackQty}}}"
