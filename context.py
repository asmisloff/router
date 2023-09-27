from typing import Dict, Tuple


MutualResistivities = Dict[Tuple[int, int], complex]


class NetworkResistanceRangeAC:
    """ 
        Такой класс в проекте уже объявлен и используется, конвертация
        из List<AcNetwork> в List<NetworkResistanceRangeAC> также есть.
    """

    def __init__(self, xMax: float, rr: MutualResistivities) -> None:
        self.xMax = xMax
        self.rr = rr


class ISchemaNode:
    """ Похожий интерфейс используется в проекте """

    def __init__(self, trackNumber: int, axisCoordinate: float, breaking=False) -> None:
        self.breaking = breaking
        self.trackNumber = trackNumber
        self.axisCoordinate = axisCoordinate
        self.duplicatedBreakingNode = False

    def __repr__(self) -> str:
        if self.breaking:
            return f"!{self.axisCoordinate}"
        if self.duplicatedBreakingNode:
            return f"~{self.axisCoordinate}"
        return str(self.axisCoordinate)

    def __eq__(self, __o: object) -> bool:
        if __o is None or type(__o) is not ISchemaNode:
            return False
        else:
            return (
                eq(self.axisCoordinate, __o.axisCoordinate) and
                self.breaking == __o.breaking and
                self.duplicatedBreakingNode == __o.duplicatedBreakingNode and
                self.trackNumber == __o.trackNumber
            )

    def __hash__(self):
        b = 1 if self.breaking else 0
        d = 1 if self.duplicatedBreakingNode else 0
        return int(100_000_000 * d + 10_000_000 * b + 1_000_000 * self.trackNumber + self.axisCoordinate)

    def copy(self, trackNumber: int = None, axisCoordinate: float = None, breaking=None):
        tn = trackNumber if trackNumber is not None else self.trackNumber
        x = axisCoordinate if axisCoordinate is not None else self.axisCoordinate
        b = breaking if breaking is not None else self.breaking
        return ISchemaNode(tn, x, b)


class ISchemaEdge:
    """ Похожий интерфейс используется в проекте """

    def __init__(self, source: ISchemaNode, target: ISchemaNode, resistance: complex = 0+0j) -> None:
        self.source = source
        self.target = target
        self.resistance = resistance

    def setConductivity(self, conductivity: float):
        self.c = conductivity

    def __repr__(self) -> str:
        return f"{self.source} -> {self.target}"


def eq(x1: float, x2: float, tol: float = 0.5e-3):
    """ Функция сравнивает числа с заданной точностью. Есть в проекте. """
    return abs(x1 - x2) <= abs(tol)
