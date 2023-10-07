from collections import deque
from dataclasses import dataclass
from functools import total_ordering
import heapq
from typing import Dict, List, Set, Tuple
import numpy as np


@total_ordering
class Node:
    def __init__(self, x: float, li: int, breaking: bool = False) -> None:
        self.x: int = round(round(x, 3) * 1000)  # до метра
        self.lineIndex: int = li
        self.breaking: bool = breaking

    def unbiasedLineIndex(self):
        return self.lineIndex % 10_000

    def branchIndex(self):
        return self.lineIndex // 10_000

    def setAxisCoordinate(self, x_: float):  # для обратной совместимости
        self.x = round(round(x_, 3) * 1000)

    def getAxisCoordinate(self) -> float:
        return round(self.x / 1000, 3)

    def copyToLineIndex(self, lineIndex: int):
        c = Node(0.0, self.lineIndex, self.breaking)
        c.x = self.x
        c.lineIndex = self.branchIndex() * 10_000 + lineIndex
        return c

    def __repr__(self) -> str:
        return str(self.x)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Node):
            return False
        return self.lineIndex == __value.lineIndex and self.x == __value.x

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, Node):
            raise TypeError()
        return self.lineIndex * 1000 + self.x < __value.lineIndex * 1000 + __value.x

    def __hash__(self) -> int:
        return self.lineIndex * 1000 + self.x


class NetworkSection:
    def __init__(self) -> None:
        self.nodes: List[Node] = []

    @classmethod
    def fromDict(cls, nodes: List[Node]) -> "NetworkSection":
        s = NetworkSection()
        s.nodes = nodes[:]
        s.nodes.sort(key=lambda n: n.lineIndex)
        return s

    def copy(self, networkChainLinkLines: Set[int], duplicateBreakinNodes: bool) -> "NetworkSection":
        c = NetworkSection()
        for n in self.nodes:
            if n.unbiasedLineIndex() in networkChainLinkLines:
                c.nodes.append(n)
                if duplicateBreakinNodes and n.breaking:
                    c.nodes[-1] = n.copyToLineIndex(n.lineIndex)
        return c

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
    def fromAcNetworkFullDto(cls, dto: List[Tuple[float, int]]) -> "BranchNetworkChain":
        xLeft = np.iinfo(np.int32).min
        chainLinks = []
        for x, trackQty in dto:
            xRight = round(round(x, 3) * 1000)
            chainLinks.append(
                BranchNetworkChainLink(
                    xLeft, xRight, set(range(1, trackQty + 1)))
            )
            xLeft = xRight
        return BranchNetworkChain(chainLinks)

    def findChainLink(self, x: int) -> BranchNetworkChainLink | None:
        idx = self.__findIndex(x)
        if idx is None:
            return None
        return self.chainLinks[idx]

    def getLines(self, x: int) -> Set[int] | None:
        idx = self.__findIndex(x)
        if idx is None:
            return None
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


def arrangeNodesByBranchIndex(nodes: Set[Node]) -> Dict[int, Dict[int, List[Node]]]:
    res: Dict[int, Dict[int, List[Node]]] = {}
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


def addNetworkChainNodes(nodes: Dict[int, Dict[int, List[Node]]], network: List[BranchNetworkChain]):
    for branchIndex, ntw in enumerate(network):
        branch = nodes[branchIndex]
        h = branch[1]
        mins = [min(h_).x for h_ in branch.values()]
        maxes = [max(h_).x for h_ in branch.values()]
        for cl in ntw.chainLinks:
            if all([cl.xRight < x for x in mins]) or all(cl.xRight > x for x in maxes):
                continue
            n = Node(cl.xRight / 1000, 1)
            if n not in h:
                heapq.heappush(h, n)


def buildBranchPartitions(branchNodeQueues: Dict[int, List[Node]], branchNetwork: BranchNetworkChain):
    partitions: List[Tuple[NetworkSection, NetworkSection]] = []

    def appendPartition():
        ntw = branchNetwork.findChainLink(out[0].nodes[0].x)
        if ntw is None:
            raise Exception("Узел вне границ ТС")
        leftSection = out.popleft().copy(ntw.lines, True)
        rightSection = out[0].copy(ntw.lines, False)
        partitions.append((leftSection, rightSection))

    allLineIndices: Set[int] = set()
    for ntw in branchNetwork.chainLinks:
        allLineIndices.update(ntw.lines)
    tmp: Dict[int, Node | None] = {key: None for key in allLineIndices}
    out: deque[NetworkSection] = deque()

    while (True):
        for key in tmp:
            tmp[key] = None
        leftMost: Node | None = None
        for li, queue in branchNodeQueues.items():
            if len(queue) > 0:
                node = heapq.heappop(queue)
                tmp[li] = node
                if leftMost is None or node.x < leftMost.x:
                    leftMost = node
        if leftMost is None:
            break
        for key, node in tmp.items():
            if node is None:
                tmp[key] = leftMost.copyToLineIndex(key)
            elif node.x > leftMost.x:
                heapq.heappush(branchNodeQueues[key], node)
                tmp[key] = leftMost.copyToLineIndex(key)
            else:
                tmp[key] = node
        if len(out) == 2:
            appendPartition()
        out.append(NetworkSection.fromDict(
            [n for n in tmp.values() if n is not None]))
    appendPartition()
    return partitions


if __name__ == "__main__":
    rng = np.random.default_rng()
    nodes: Set[Node] = set()
    network: List[BranchNetworkChain] = []
    for branchIndex in range(3):
        for i in range(1, 4):
            nodes.update([Node(x, 10_000 * branchIndex + i)
                         for x in rng.random(i + 1) * 100])
        network.append(BranchNetworkChain.fromAcNetworkFullDto([(x, 2) for x in rng.random(2) * 150]))

    print(f"network: {network}")
    nodeQueues = arrangeNodesByBranchIndex(nodes)
    print(f"nodeQueues: {nodeQueues}")
    addNetworkChainNodes(nodeQueues, network)

    partitions = buildBranchPartitions(nodeQueues[0], network[0])
    print(partitions)
