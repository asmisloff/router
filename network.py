from dataclasses import dataclass
from typing import Dict, List, Set
import numpy as np

from context import AcNetwork, AcNetworkLattice, ISchemaNode


class NetworkSection:
    def __init__(self) -> None:
        self.nodes: List[ISchemaNode] = []
        self.__idx = -1

    def size(self):
        return len(self.nodes)

    def get(self, idx: int) -> ISchemaNode:
        return self.nodes[idx]
    
    def deepCopy(self) -> "NetworkSection":
        cp = NetworkSection()
        for n in self.nodes:
            cp.nodes.append(ISchemaNode.createInstance(n.x, n.branchIndex(), n.relativeLineIndex()))
        return cp

    def __iter__(self):
        self.__idx = -1
        return self

    def __next__(self) -> ISchemaNode:
        self.__idx += 1
        if self.__idx < len(self.nodes):
            return self.nodes[self.__idx]
        raise StopIteration

    def __repr__(self) -> str:
        return str([n for n in self.nodes])


@dataclass
class BranchNetworkChainLink:
    xLeft: int
    xRight: int
    lines: Set[int]
    lattice: AcNetworkLattice


class BranchNetworkChain:
    def __init__(self, chainLinks: List[BranchNetworkChainLink]) -> None:
        self.chainLinks = sorted(chainLinks, key=lambda cl: cl.xRight)
        self.__idx = 0

    @classmethod
    def fromAcNetwork(cls, networks: List[AcNetwork]) -> "BranchNetworkChain":
        xLeft = np.iinfo(np.int32).min
        chainLinks = []
        for ntw in networks:
            x = ntw.coordinate
            trackQty = ntw.trackQty
            xRight = round(round(x, 3) * 1000)
            chainLinks.append(
                BranchNetworkChainLink(
                    xLeft, xRight, set(range(1, trackQty + 1)), AcNetworkLattice())
            )
            xLeft = xRight
        return BranchNetworkChain(chainLinks)

    def findChainLink(self, x: int) -> BranchNetworkChainLink:
        idx = self.__findIndex(x)
        if idx is None:
            raise Exception(f"Точка за границами КС -- {x}")
        return self.chainLinks[idx]

    def getCurrent(self) -> BranchNetworkChainLink:
        return self.chainLinks[self.__idx]

    def first(self):
        return self.chainLinks[0]

    def last(self):
        return self.chainLinks[-1]

    def getLines(self, x: int) -> Set[int]:
        idx = self.__findIndex(x)
        if idx is None:
            raise Exception(f"Точка за границами КС -- {x}")
        cl = self.chainLinks[idx]
        if cl.xRight == x and idx != len(self.chainLinks) - 1:
            clr = self.chainLinks[idx + 1]
            return cl.lines.union(clr.lines)
        return cl.lines

    def __findIndex(self, x: int) -> int | None:
        cl = self.chainLinks[self.__idx]
        if x == cl.xLeft:
            return self.__idx - 1
        elif cl.xRight == x:
            if self.__idx < len(self.chainLinks) - 1:
                self.__idx += 1
            return self.__idx
        elif x > self.chainLinks[-1].xRight:
            return None
        elif x < cl.xLeft:
            self.__idx -= 1
            return self.__findIndex(x)
        elif x > cl.xRight:
            self.__idx += 1
            return self.__findIndex(x)
        else:  # x > cl.xLeft and x < cl.xRight
            return self.__idx

    def __repr__(self) -> str:
        return "_".join(str(cl.xRight) for cl in self.chainLinks)

