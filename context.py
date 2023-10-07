from enum import Enum
from functools import total_ordering
from typing import Dict, Tuple


MutualResistivities = Dict[Tuple[int, int], complex]


class Side(Enum):
    Left = 0
    Right = 1


class AcNetworkLattice:
    def cond(
        self,
        lineIndex1: int,
        side1: Side,
        lineIndex2: int,
        side2: Side,
        length: float
    ) -> complex:
        return 0 + 0j


class NetworkResistanceRangeAC:
    """ 
        Такой класс в проекте уже объявлен и используется, конвертация
        из List<AcNetwork> в List<NetworkResistanceRangeAC> также есть.
    """

    def __init__(self, xMax: float, rr: MutualResistivities) -> None:
        self.xMax = xMax
        self.rr = rr


@total_ordering
class ISchemaNode:
    """ Похожий интерфейс используется в проекте """

    def __init__(self, lineIndex: int, axisCoordinate: float, breaking=False) -> None:
        self.breaking = breaking
        self.lineIndex = lineIndex
        self.x = round(axisCoordinate * 1000)
        self.duplicatedBreakingNode = False

    @classmethod
    def createInstance(cls, x: int, branchIndex: int, lineIndex: int) -> "ISchemaNode":
        return ISchemaNode(branchIndex * 10_000 + lineIndex, 1e-3 * x)

    def axisCoordinate(self) -> float:
        return round(self.x / 1000, 3)

    def __repr__(self) -> str:
        if self.breaking:
            return f"!{self.x}"
        if self.duplicatedBreakingNode:
            return f"~{self.x}"
        return str(self.x)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ISchemaNode):
            return False
        if self.lineIndex % 10_000 == 0:
            return __value.lineIndex % 10_000 == 0
        return self.lineIndex == __value.lineIndex and self.x == __value.x

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, ISchemaNode):
            raise TypeError()
        return self.lineIndex * 1000 + self.x < __value.lineIndex * 1000 + __value.x

    def __hash__(self):
        b = 1 if self.breaking else 0
        d = 1 if self.duplicatedBreakingNode else 0
        return int(100_000_000 * d + 10_000_000 * b + 1_000_000 * self.lineIndex + self.axisCoordinate())


class ISchemaEdge:
    """ Похожий интерфейс используется в проекте """

    def __init__(self, resistance: complex = 1+0j) -> None:
        self.__source: ISchemaNode | None = None
        self.__target: ISchemaNode | None = None
        self.c = 1 / resistance

    @classmethod
    def createWithCond(cls, c: complex) -> "ISchemaEdge":
        return ISchemaEdge(1 / c)

    def setConductivity(self, conductivity: float):
        self.c = conductivity

    def getSourceNode(self) -> ISchemaNode:
        if (self.__source is None):
            raise Exception("Ребро не было добавлено в граф")
        return self.__source

    def getTargetNode(self) -> ISchemaNode:
        if (self.__target is None):
            raise Exception("Ребро не было добавлено в граф")
        return self.__target

    def __repr__(self) -> str:
        return f"{self.__source} -> {self.__target}"


class Payload:
    def __init__(self, x: float) -> None:
        self.x: int = round(x * 1000)
        self.trackNumber: int = 1
        self.iplEdge: ISchemaEdge = ISchemaEdge()

    def __repr__(self) -> str:
        return f"{{x: {self.x}, li: {self.trackNumber % 10_000}, br: {self.trackNumber // 10_000}}}"


class AcNetwork:
    def __init__(self, coordinate: float, trackQty: int = 2) -> None:
        self.coordinate = coordinate
        self.trackQty = trackQty
