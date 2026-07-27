from collections import defaultdict
from typing import DefaultDict


class Graph:

    def __init__(self, hubs: dict, connections: list):
        """Maps out the graph's hubs and connections"""

        self.hubs = hubs

        self.graph: DefaultDict[str, list[tuple[str, int]]] = defaultdict(list)

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
