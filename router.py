import heapq
from itertools import combinations
from typing import Dict, List, Set

import numpy as np
from context import AcNetworkDto, ICircuitEdge, ICircuitNode
from graph import Graph
from partition import Partition
from network import BranchNetworkChain, NetworkSection


class Router:
    """ Трассировщик """

    def __init__(self, graph: Graph, networks: Dict[int, List[AcNetworkDto]]) -> None:
        self.__graph = graph
        self.__network: Dict[int, BranchNetworkChain] = {
            li: BranchNetworkChain.fromAcNetworkDto(ntw) for li, ntw in networks.items()
        }
        self.partitions: Dict[int, List[Partition]] = {}

    def buildPartitions(self):
        """ Построить разделы ТС """
        for branchIndex in self.__network.keys():
            self.partitions[branchIndex] = self.__buildBranchPartitions(
                self.__arrangeNodesByBranchIndex(self.__graph.nodes()),
                self.__network,
                branchIndex
            )

    def initCells(self):
        for partitions in self.partitions.values():
            for p in partitions:
                p.initCells()

    def __buildBranchPartitions(self, branches: Dict[int, Dict[int, List[ICircuitNode]]], network: Dict[int, BranchNetworkChain], branchIndex: int) -> List[Partition]:
        branchNodeQueues = branches[branchIndex]
        branchNetwork = network[branchIndex]
        partitions: List[Partition] = []
        zeroNode = ICircuitNode(0, 0)

        leftBound = min((min(q) for q in branchNodeQueues.values())).x
        rightBound = max((max(q) for q in branchNodeQueues.values())).x
        if branchNetwork.last().xRight < rightBound:
            rightBound = branchNetwork.last().xRight

        leftSection: Dict[int, ICircuitNode] = {}
        for li in branchNetwork.findChainLink(leftBound).lines:
            q = branchNodeQueues.get(li)
            if q is None or len(q) == 0:
                leftSection[li] = ICircuitNode.createInstance(
                    leftBound, branchIndex, li)
            else:
                n = heapq.heappop(q)
                if n.x > leftBound:
                    heapq.heappush(q, n)
                    leftSection[li] = ICircuitNode.createInstance(
                        leftBound, branchIndex, + li)
                else:
                    leftSection[li] = n

        while (leftBound < rightBound):
            leftMost = rightBound
            rightSection: Dict[int, ICircuitNode] = {}
            cl = branchNetwork.findChainLink(leftBound)
            defaultX = min(cl.xRight, rightBound)
            ls = NetworkSection([])
            rs = NetworkSection([])
            for li in cl.lines:
                q = branchNodeQueues.get(li)
                node: ICircuitNode
                if q is None or len(q) == 0:
                    node = ICircuitNode.createInstance(
                        defaultX, branchIndex, + li)
                else:
                    n = heapq.heappop(q)
                    while n.x < leftBound:
                        n = heapq.heappop(q)
                    if n.x > defaultX:
                        heapq.heappush(q, n)
                        node = ICircuitNode.createInstance(
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
                        rightSection[li] = ICircuitNode.createInstance(
                            leftMost, branchIndex, li)
                rs.nodes.append(rightSection[li])
                ls.nodes.append(
                    self.__copyIfBreaking(
                        leftSection.get(li) or
                        ICircuitNode.createInstance(leftBound, branchIndex, li)
                    )
                )
            partitions.append(Partition(leftBound, leftMost,
                              ls, rs, zeroNode, cl.lattice, self.__graph))
            leftSection = rightSection
            leftBound = leftMost

        return partitions

    def __arrangeNodesByBranchIndex(self, nodes: Set[ICircuitNode]) -> Dict[int, Dict[int, List[ICircuitNode]]]:
        res: Dict[int, Dict[int, List[ICircuitNode]]] = {}
        for node in nodes:
            branchIndex = node.branchIndex()
            branch = res.get(branchIndex)
            if branch is None:
                branch = {}
                res[branchIndex] = branch
            li = node.relativeLineIndex()
            h = branch.get(li)
            if h is None:
                h = []
                heapq.heapify(h)
                branch[li] = h
            if node not in h:
                heapq.heappush(h, node)
        return res

    def __copyIfBreaking(self, node: ICircuitNode) -> ICircuitNode:
        if node.breaking:
            cp = ICircuitNode(node.lineIndex, node.axisCoordinate(), False)
            cp.duplicatedBreakingNode = True
            return cp
        return node


if __name__ == "__main__":
    rng = np.random.default_rng()
    nodes: Set[ICircuitNode] = set()
    networks: Dict[int, List[AcNetworkDto]] = {}
    for branchIndex in range(3):
        for i in range(1, 4):
            nodes.update([ICircuitNode(10_000 * branchIndex + i, x)
                         for x in rng.random(i + 1) * 100])
        networks[branchIndex] = [AcNetworkDto(x, 2) for x in rng.random(2) * 150]

    graph = Graph(nodes)
    print(f"main schema network: {networks[0]}")
    router = Router(graph, networks)
    router.buildPartitions()
    print(f"main schema nodes: {[n for n in nodes if n.branchIndex() == 0]}")

    print(router.partitions[0])
