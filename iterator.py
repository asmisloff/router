from typing import Deque, Dict, List, Tuple
from context import ISchemaNode, NetworkResistanceRangeAC, eq
from collections import deque


class SectionNodeIterator:
    """
        Итератор по параллельным сечениям.
        При каждом вызове возвращает два списка узлов: левого сечения и правого сечения.
        Сечение строится через каждую координату на К и/или П линиях, в которую установлен узел.
        Если на какой-то линии в текущем сечении нет узла, итератор создаст новый.
        Визуализацию см. в router_test.py.
    """

    def __init__(self, branchCnNodes: Dict[int, Deque[ISchemaNode]]) -> None:
        """ branchCnNodes - узлы К и П линий схемы ветви. Ключи - индексы линий, значения - очереди узлов по возрастанию координаты. """
        self.__cnNodes = branchCnNodes

    def __iter__(self):
        self.__right: Dict[int, ISchemaNode] = {tn: None for tn in self.__cnNodes}
        self.__left: Dict[int, ISchemaNode] = {tn: None for tn in self.__cnNodes}
        self.__cnt = 0
        return self

    def __next__(self) -> Tuple[Dict[int, ISchemaNode], Dict[int, ISchemaNode]]:
        leftMostNode: ISchemaNode = None
        tmp = self.__left
        self.__left = self.__right
        self.__right = tmp
        self.__substituteBreakingNodes(self.__left)
        for tn, q in self.__cnNodes.items():
            node = q.popleft() if len(q) > 0 else None
            self.__right[tn] = node
            if node is not None:
                if leftMostNode is None or node.axisCoordinate < leftMostNode.axisCoordinate:
                    leftMostNode = node

        if leftMostNode is None:
            raise StopIteration

        for tn, q in self.__cnNodes.items():
            node = self.__right[tn]
            if node is None:
                self.__right[tn] = leftMostNode.copy(trackNumber=tn, breaking=False)
            elif not eq(node.axisCoordinate, leftMostNode.axisCoordinate):
                q.appendleft(self.__right[tn])
                self.__right[tn] = leftMostNode.copy(trackNumber=tn, breaking=False)

        self.__cnt += 1
        if self.__cnt == 1:
            return self.__next__()
        else:
            return self.__left, self.__right

    def __substituteBreakingNodes(self, d: Dict[int, ISchemaNode]) -> None:
        for i, n in d.items():
            if n is not None and n.breaking:
                clone = ISchemaNode(n.trackNumber, n.axisCoordinate)
                clone.duplicatedBreakingNode = True
                d[i] = clone
