from collections import defaultdict


# neighbor -> edge capacity
class Zone:
    def __init__(self, name, cost=1, max_drones=1):
        self.name = name
        self.cost = cost
        self.max_drones = max_drones
        self.neighbors = {}


class Graph:

    def __init__(self, hubs, connections):

        self.hubs = hubs

        # adjacency list
        self.graph = defaultdict(list)

        # edge capacities
        self.cap = defaultdict(dict)

        for con in connections:

            self.graph[con.from_hub].append(
                (con.to_hub, con.max_link_cap)
            )
            self.graph[con.to_hub].append(
                (con.from_hub, con.max_link_cap)
            )
            self.cap[con.from_hub][con.to_hub] = con.max_link_cap
            self.cap[con.to_hub][con.from_hub] = con.max_link_cap
