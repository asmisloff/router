from collections import deque
from dataclasses import dataclass
from functools import total_ordering
import heapq
from typing import Dict, List, Set, Tuple
import numpy as np

from context import AcNetwork, ISchemaNode


class NetworkSection:
    def __init__(self) -> None:
        self.nodes: List[ISchemaNode] = []
        self.__idx = 0

    def size(self):
        return len(self.nodes)

    def get(self, idx: int) -> ISchemaNode:
        return self.nodes[idx]

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self) -> ISchemaNode:
        if self.__idx < len(self.nodes):
            return self.nodes[self.__idx]
        raise StopIteration

    def __repr__(self) -> str:
        return str([n.x for n in self.nodes])


@dataclass
class BranchNetworkChainLink:
    xLeft: int
    xRight: int
    lines: Set[int]


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
                    xLeft, xRight, set(range(1, trackQty + 1)))
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


def arrangeNodesByBranchIndex(nodes: Set[ISchemaNode]) -> Dict[int, Dict[int, List[ISchemaNode]]]:
    res: Dict[int, Dict[int, List[ISchemaNode]]] = {}
    for node in nodes:
        branchIndex = node.lineIndex // 10_000
        branch = res.get(branchIndex)
        if branch is None:
            branch = {}
            res[branchIndex] = branch
        li = node.lineIndex % 10_000
        h = branch.get(li)
        if h is None:
            h = []
            heapq.heapify(h)
            branch[li] = h
        if node not in h:
            heapq.heappush(h, node)
    return res


def copyIfBreaking(node: ISchemaNode) -> ISchemaNode:
    if node.breaking:
        cp = ISchemaNode(node.lineIndex, node.axisCoordinate(), False)
        cp.duplicatedBreakingNode = True
        return cp
    return node


def buildBranchPartitions(branches: Dict[int, Dict[int, List[ISchemaNode]]], network: Dict[int, BranchNetworkChain], branchIndex: int):
    branchNodeQueues = branches[branchIndex]
    branchNetwork = network[branchIndex]
    partitions: List[Tuple[NetworkSection, NetworkSection]] = []

    leftBound = min((min(q) for q in branchNodeQueues.values())).x
    rightBound = max((max(q) for q in branchNodeQueues.values())).x
    if branchNetwork.last().xRight < rightBound:
        rightBound = branchNetwork.last().xRight

    leftSection: Dict[int, ISchemaNode] = {}
    for li in branchNetwork.findChainLink(leftBound).lines:
        q = branchNodeQueues.get(li)
        if q is None or len(q) == 0:
            leftSection[li] = ISchemaNode.createInstance(
                leftBound, branchIndex, li)
        else:
            n = heapq.heappop(q)
            if n.x > leftBound:
                heapq.heappush(q, n)
                leftSection[li] = ISchemaNode.createInstance(
                    leftBound, branchIndex, + li)
            else:
                leftSection[li] = n

    while (leftBound < rightBound):
        leftMost = rightBound
        rightSection: Dict[int, ISchemaNode] = {}
        cl = branchNetwork.findChainLink(leftBound)
        defaultX = min(cl.xRight, rightBound)
        ls = NetworkSection()
        rs = NetworkSection()
        for li in cl.lines:
            q = branchNodeQueues.get(li)
            node: ISchemaNode
            if q is None or len(q) == 0:
                node = ISchemaNode.createInstance(defaultX, branchIndex, + li)
            else:
                n = heapq.heappop(q)
                while n.x < leftBound:
                    n = heapq.heappop(q)
                if n.x > defaultX:
                    heapq.heappush(q, n)
                    node = ISchemaNode.createInstance(
                        defaultX, branchIndex, li)
                else:
                    node = n
            rightSection[li] = node
            if node.x < leftMost:
                leftMost = node.x
        for li in cl.lines:
            node = rightSection[li]
            if node.x > leftMost:
                q = branchNodeQueues.get(li)
                if q is None:
                    node.x = leftMost
                else:
                    heapq.heappush(q, node)
                    rightSection[li] = ISchemaNode.createInstance(
                        leftMost, branchIndex, li)
            rs.nodes.append(rightSection[li])
            ls.nodes.append(
                copyIfBreaking(
                    leftSection.get(li) or
                    ISchemaNode.createInstance(leftBound, branchIndex, li))
            )
        partitions.append((ls, rs))
        leftSection = rightSection
        leftBound = leftMost

    return partitions


if __name__ == "__main__":
    rng = np.random.default_rng()
    nodes: Set[ISchemaNode] = set()
    network: Dict[int, BranchNetworkChain] = {}
    for branchIndex in range(3):
        for i in range(1, 4):
            nodes.update([ISchemaNode(10_000 * branchIndex + i, x)
                         for x in rng.random(i + 1) * 100])
        network[branchIndex] = BranchNetworkChain.fromAcNetwork(
            [AcNetwork(x, 2) for x in rng.random(2) * 150]
        )

    print(f"network: {network[0]}")
    nodeQueues = arrangeNodesByBranchIndex(nodes)
    print(f"nodeQueues: {nodeQueues[0]}")
    # addNetworkChainNodes(nodeQueues, network)

    partitions = buildBranchPartitions(nodeQueues, network, 0)
    print(partitions)
