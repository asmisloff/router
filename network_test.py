from context import NetworkResistanceRangeAC
from network import Network
import unittest


class Test(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def testGetResistance(self):
        ranges = {
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
                    xMax=20,
                    rr={
                        (1, 1): 1.2+1.2j,
                        (2, 2): 2.2+2.2j,
                        (3, 3): 3.2+3.2j
                    }
                ),
                NetworkResistanceRangeAC(
                    xMax=30,
                    rr={
                        (1, 1): 1.3+1.3j,
                        (2, 2): 2.3+2.3j,
                        (3, 3): 3.3+3.3j
                    }
                )
            ]
        }

        network = Network(ranges)
        self.assertEqual(
            {(1, 1): (24+24j), (2, 2): (44+44j), (3, 3): (64+64j)},
            network.getResistances(0, 5, 25)
        )


if __name__ == "__main__":
    unittest.main()
