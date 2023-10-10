import unittest
from context import AcNetworkDto, ICircuitNode
from graph import Graph
from router import Router


class RouterTest(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName)

    def test(self):
        np = nodeProducer(1)
        n1 = [np(1), np(2, True), np(5), np(13), np(15), np(20)]

        np = nodeProducer(2)
        n2 = [np(0), np(2, True), np(4), np(5)]

        np = nodeProducer(3)
        n3 = [np(2, True), np(6), np(17), np(22, True), np(25)]

        graph = Graph(n1 + n2 + n3)

        ntw = {0: [AcNetworkDto(10, 3), AcNetworkDto(21, 2), AcNetworkDto(24, 3)]}

        r = Router(graph, ntw)
        r.buildPartitions()
        # for partitions in r.partitions.values():
        #     for p in partitions:
        #         p._Partition__capacity = 2  # type: ignore
        r.initCells()
        # for partitions in r.partitions.values():
        #     for p in partitions:
        #         if p.firstCell is not None:
        #             p.firstCell.pullRightSection((p.xRight + p.xLeft) // 2)

        print(r.partitions[0])
        print(sorted(graph.nodes()))
        graph.plot(showZeroNode=False, shift=0.1)


def nodeProducer(tn: int):
    def _f(x: float, breaking=False):
        return ICircuitNode(tn, x, breaking)
    return _f


if __name__ == "__main__":
    unittest.main()
