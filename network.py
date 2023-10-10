from dataclasses import dataclass
from typing import Dict, List, Set
import numpy as np

from context import AcNetworkDto, AcNetworkLattice, ICircuitNode


class NetworkSection:
    def __init__(self, nodes: List[ICircuitNode]) -> None:
        self.nodes: List[ICircuitNode] = nodes
        self.__idx = -1

    def size(self):
        return len(self.nodes)

    def get(self, idx: int) -> ICircuitNode:
        return self.nodes[idx]
    
    def deepCopy(self) -> "NetworkSection":
        cp = NetworkSection([])
        for n in self.nodes:
            cp.nodes.append(ICircuitNode.createInstance(n.x, n.branchIndex(), n.relativeLineIndex()))
        return cp

    def __iter__(self):
        self.__idx = -1
        return self

    def __next__(self) -> ICircuitNode:
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
    def fromAcNetworkDto(cls, networks: List[AcNetworkDto]) -> "BranchNetworkChain":
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

    def last(self):
        return self.chainLinks[-1]

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

