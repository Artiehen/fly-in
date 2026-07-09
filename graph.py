from collections import defaultdict
from typing import DefaultDict


# neighbor -> edge capacity
class Zone:
    def __init__(self, name: str, cost: int = 1, max_drones: int = 1):
        self.name: str = name
        self.cost: int = cost
        self.max_drones: int = max_drones
        self.neighbors: dict[str, int] = {}


class Graph:

    def __init__(self, hubs: dict, connections: list):

        self.hubs = hubs

        # adjacency list
        self.graph: DefaultDict[str, list[tuple[str, int]]] = defaultdict(list)

        # edge capacities
        self.cap: DefaultDict[str, dict[str, int]] = defaultdict(dict)
        for con in connections:

            self.graph[con.from_hub].append(
                (con.to_hub, con.max_link_cap)
            )
            self.graph[con.to_hub].append(
                (con.from_hub, con.max_link_cap)
            )
            self.cap[con.from_hub][con.to_hub] = con.max_link_cap
            self.cap[con.to_hub][con.from_hub] = con.max_link_cap
