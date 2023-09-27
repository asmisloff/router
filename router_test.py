import unittest
from context import ISchemaNode, NetworkResistanceRangeAC
from graph import Graph
from network import Network
from router import Router
from typing import Callable, Optional


class RouterTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test(self):
        np = nodeProducer(1)
        n1 = [np(1), np(2, True), np(5), np(13), np(15), np(20)]

        np = nodeProducer(2)
        n2 = [np(0), np(2, True), np(4), np(5)]

        np = nodeProducer(3)
        n3 = [np(2, True), np(6), np(17), np(22, True), np(25)]

        graph = Graph(n1 + n2 + n3)

        ntw = Network(
            {
                0: [
                    NetworkResistanceRangeAC(
                        xMax=10,
                        rr={
                            (1, 1): 1.1+1.1j,
                            (2, 2): 2.1+2.1j,
                            (3, 3): 3.1+3.1j
                        }
                    ),
                    NetworkResistanceRangeAC(
                        xMax=21,
                        rr={
                            (1, 1): 1.2+1.2j,
                            (2, 2): 2.2+2.2j,
                            (3, 3): 3.2+3.2j
                        }
                    ),
                    NetworkResistanceRangeAC(
                        xMax=24,
                        rr={
                            (1, 1): 1.3+1.3j,
                            (2, 2): 2.3+2.3j,
                            (3, 3): 3.3+3.3j
                        }
                    )
                ]
            }
        )

        r = Router(graph, ntw)
        r.wire()

        graph.plot(0.1)


def nodeProducer(tn: int):
    def _f(x: int, breaking=False):
        return ISchemaNode(tn, x, breaking)
    return _f


if __name__ == "__main__":
    unittest.main()
