import unittest
from context import AcNetwork, ISchemaNode
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

        ntw = {0: [AcNetwork(10, 3), AcNetwork(21, 2), AcNetwork(26, 3)]}

        r = Router(graph, ntw)
        r.wire()

        graph.plot(0.1)


def nodeProducer(tn: int):
    def _f(x: int, breaking=False):
        return ISchemaNode(tn, x, breaking)
    return _f


if __name__ == "__main__":
    unittest.main()
