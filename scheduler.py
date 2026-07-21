import heapq
from collections import defaultdict
from colorama import Fore, init
# from typing import Any
from graph import Graph
from fileparser import MapData
from drones import Drone

init(autoreset=True)

ZONE_COST = {
    "normal": 1,
    "priority": 1,
    "restricted": 3,
    "blocked": float("inf")
}


def heuristic(hubs: dict[str, MapData], a: str, b: str) -> int:
    """Manhattan distance using coordinates"""
    ha = hubs[a]
    hb = hubs[b]
    return abs(ha.x - hb.x) + abs(ha.y - hb.y)


def astar(graph: Graph, hubs: dict[str, MapData],
          start: str, goal: str) -> list[str]:
    """A* shortest path"""

    pq: list[tuple[float, str]] = [(0, start)]
    came_from: dict[str, str | None] = {start: None}
    cost_so_far: dict[str, float] = {start: 0}
    came_from[start] = None

    while pq:

        _, current = heapq.heappop(pq)

        if current == goal:
            break

        for neighbor, _cap in graph.graph[current]:

            zone = hubs[neighbor]

            move_cost = ZONE_COST.get(zone.zone, 1)

            if move_cost == float("inf"):
                continue

            new_cost = cost_so_far[current] + move_cost

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:

                cost_so_far[neighbor] = new_cost

                priority = new_cost + heuristic(hubs, neighbor, goal)

                heapq.heappush(pq, (priority, neighbor))

                came_from[neighbor] = current

    if goal not in came_from:
        return []

    # reconstruct path
    path: list = []
    node: str | None = goal

    while node is not None:
        path.append(node)
        node = came_from[node]

    path.reverse()

    return path


class Scheduler:

    def __init__(self, graph: Graph, hubs: dict[str, MapData],
                 drones: list[Drone]) -> None:

        self.graph: Graph = graph
        self.hubs: dict[str, MapData] = hubs
        self.drones: list[Drone] = drones
        self.frames: list[dict[str, str]] = []

        self.turn: int = 0

        # occupancy tracking
        self.zone_occupancy: defaultdict[str, int] = defaultdict(int)

    def all_finished(self) -> bool:
        return all(d.finished for d in self.drones)

    def plan_paths(self) -> None:
        for d in self.drones:
            d.path = astar(self.graph, self.hubs, d.position, d.goal)

    def rebuild_occupancy(self) -> None:
        self.zone_occupancy.clear()

        for d in self.drones:
            if not d.finished:
                self.zone_occupancy[d.position] += 1

    def can_move(self, drone: Drone, next_node: str,
                 edge_reservation: defaultdict[tuple[str, str], int]) -> bool:

        hub = self.hubs[next_node]

        # zone capacity check
        if self.zone_occupancy[next_node] >= hub.max_drones:
            return False

        # edge capacity check
        current = drone.position
        edge: tuple[str, str]

        if current < next_node:
            edge = (current, next_node)
        else:
            edge = (next_node, current)

        graph_cap = self.graph.cap[current][next_node]

        if edge_reservation[edge] >= graph_cap:
            return False

        return True

    def move_drone(self, drone: Drone, next_node: str,
                   edge_reservation: defaultdict[tuple[str, str], int]) -> str:

        current = drone.position

        if current < next_node:
            edge: tuple[str, str] = (current, next_node)
        else:
            edge = (next_node, current)

        edge_reservation[edge] += 1

        self.zone_occupancy[current] -= 1
        self.zone_occupancy[next_node] += 1

        drone.position = next_node

        return next_node

    def run(self) -> None:

        self.plan_paths()
        self.rebuild_occupancy()

        while not self.all_finished():
            self.save_frame()

            self.turn += 1

            # print(Fore.CYAN + f"\n===== TURN {self.turn} =====")

            edge_res: defaultdict[tuple[str, str], int] = defaultdict(int)

            self.rebuild_occupancy()

            turn_moves: list[str] = []

            for drone in self.drones:

                if drone.finished:
                    continue

                # if path invalid → recompute (dynamic replanning)
                if (
                    not drone.path
                    or drone.position not in drone.path
                ):
                    drone.path = astar(
                        self.graph,
                        self.hubs,
                        drone.position,
                        drone.goal
                    )

                idx = drone.path.index(drone.position)

                if idx + 1 >= len(drone.path):
                    drone.finished = True
                    continue

                nxt = drone.path[idx + 1]

                if self.can_move(drone, nxt, edge_res):
                    next_node = self.move_drone(drone, nxt, edge_res)
                    turn_moves.append(f"D{drone.id}-{next_node}")
                    if drone.position == drone.goal:
                        drone.finished = True

            if turn_moves:
                print(Fore.YELLOW + " ".join(turn_moves))
        self.save_frame()

    def save_frame(self) -> None:
        frame: dict[str, str] = {}

        for drone in self.drones:
            frame[str(drone.id)] = drone.position

        self.frames.append(frame)
