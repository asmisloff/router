from collections import deque
from functools import total_ordering
import heapq
from typing import Callable, Dict, Iterable, List, Set, Tuple, TypeVar
import numpy as np

@total_ordering
class Node:
    def __init__(self, x: float, li: int, breaking: bool = False) -> None:
        self.x: int = round(round(x, 3) * 1000) # до метра
        self.lineIndex: int = li
        self.breaking: bool = breaking

    def unbiasedLineIndex(self):
        return self.lineIndex % 10_000

    def branchIndex(self):
        return self.lineIndex // 10_000

    def setAxisCoordinate(self, x_: float): # для обратной совместимости
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
        s.nodes.sort(key = lambda n: n.lineIndex)
        return s
    
    def copy(self, networkChainLinkLines: Set[int], duplicateBreakinNodes: bool) -> "NetworkSection":
        c = NetworkSection()
        for n in self.nodes:
            if n.unbiasedLineIndex() in networkChainLinkLines:
                c.nodes.append(n)
                if duplicateBreakinNodes and n.breaking:
                    c.nodes[-1] = n.copyToLineIndex(n.lineIndex)
        return c

    def size(self):
        return len(self.nodes)
    
    def __repr__(self) -> str:
        return str([n.x for n in self.nodes])


class BranchNetworkChainLink:
    def __init__(self, xRight: float, lines: Set[int]) -> None:
        self.xRight: int = round(round(xRight, 3) * 1000)
        self.lines = lines


class BranchNetworkChain:
    def __init__(self, chainLinks: List[BranchNetworkChainLink]) -> None:
        self.chainLinks = sorted(chainLinks, key=lambda cl: cl.xRight)
    
    def findChainLink(self, x: int) -> BranchNetworkChainLink | None:
        for cl in self.chainLinks:
            if cl.xRight >= x:
                return cl
        return None
    
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
    tmp: Dict[int, Node | None] = {key : None for key in allLineIndices}
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
        out.append(NetworkSection.fromDict([n for n in tmp.values() if n is not None]))
    appendPartition()
    return partitions


if __name__ == "__main__":
    rng = np.random.default_rng()
    nodes: Set[Node] = set()
    network: List[BranchNetworkChain] = []
    for branchIndex in range(3):
        for i in range(1, 4):
            nodes.update([Node(x, 10_000 * branchIndex + i) for x in rng.random(i + 1) * 100])
        network.append(
            BranchNetworkChain(
                [BranchNetworkChainLink(x, set((1, 2))) for x in rng.random(2) * 100]
            )
        )

    print(network)
    nodeQueues = arrangeNodesByBranchIndex(nodes)
    print(nodeQueues)
    addNetworkChainNodes(nodeQueues, network)
    
    partitions = buildBranchPartitions(nodeQueues[0], network[0])
    print(partitions)