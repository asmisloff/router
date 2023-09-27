from typing import Dict, List
from context import NetworkResistanceRangeAC


class Network:
    """ Представление тяговой сети в удобной для трассировщика форме. """

    def __init__(self, rangesByBranchIndex: Dict[int, List[NetworkResistanceRangeAC]]) -> None:
        self.rangesByBranchIndex = rangesByBranchIndex
        self.__dict = {}

    def getResistances(self, branchIndex: int, x1: float, x2: float) -> Dict[int, complex]:
        """
            Возвращает хэш-таблицу с собственными и взаимными сопротивлениями для участка КС
            между координатами x1 и x2. Похожая функция уже есть в проекте, но в такой форме,
            кажется, будет удобнее.
        """
        self.__dict.clear()
        xLeft = x1
        xRight = x2
        try:
            branchRanges = self.rangesByBranchIndex[branchIndex]
        except KeyError:
            raise Exception(f"КС не определены для ответвления с индексом {branchIndex}")
        for r in branchRanges:
            if r.xMax <= xLeft:
                continue
            elif r.xMax >= xRight:
                dx = xRight - xLeft
                for tn, mr in r.rr.items():
                    if tn not in self.__dict:
                        self.__dict[tn] = 0+0j
                    self.__dict[tn] += (mr * dx)
                return self.__dict
            elif r.xMax > xLeft and r.xMax < xRight:
                dx = r.xMax - xLeft
                xLeft = r.xMax
                for tn, mr in r.rr.items():
                    if tn not in self.__dict:
                        self.__dict[tn] = 0+0j
                    self.__dict[tn] += (mr * dx)
        raise Exception(
            f"Контактная сеть не определена для интервала координат {xLeft}-{xRight}"
        )
