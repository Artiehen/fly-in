import heapq
from collections import defaultdict
from colorama import Fore, init

init(autoreset=True)

ZONE_COST = {
    "normal": 1,
    "priority": 1,
    "restricted": 3,
    "blocked": float("inf")
}


# =========================
# A* PATHFINDING
# =========================
def heuristic(hubs, a, b):
    """Manhattan distance using coordinates"""
    ha = hubs[a]
    hb = hubs[b]
    return abs(ha.x - hb.x) + abs(ha.y - hb.y)


def astar(graph, hubs, start, goal):
    """A* shortest path"""

    pq = [(0, start)]

    came_from = {}
    cost_so_far = {start: 0}

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
    path = []
    node = goal

    while node is not None:
        path.append(node)
        node = came_from[node]

    path.reverse()

    return path


# =========================
# SCHEDULER
# =========================
class Scheduler:

    def __init__(self, graph, hubs, drones):

        self.graph = graph
        self.hubs = hubs
        self.drones = drones
        self.frames = []

        self.turn = 0

        # occupancy tracking
        self.zone_occupancy = defaultdict(int)

    # -------------------------
    def all_finished(self):
        return all(d.finished for d in self.drones)

    # -------------------------
    def plan_paths(self):
        for d in self.drones:
            d.path = astar(self.graph, self.hubs, d.position, d.goal)

    # -------------------------
    def rebuild_occupancy(self):
        self.zone_occupancy.clear()

        for d in self.drones:
            if not d.finished:
                self.zone_occupancy[d.position] += 1

    # -------------------------
    def can_move(self, drone, next_node, edge_reservation):

        hub = self.hubs[next_node]

        # zone capacity check
        if self.zone_occupancy[next_node] >= hub.max_drones:
            return False

        # edge capacity check
        current = drone.position
        edge = tuple(sorted((current, next_node)))

        graph_cap = self.graph.cap[current][next_node]

        if edge_reservation[edge] >= graph_cap:
            return False

        return True

    # -------------------------
    def move_drone(self, drone, next_node, edge_reservation):

        current = drone.position

        edge = tuple(sorted((current, next_node)))

        edge_reservation[edge] += 1

        self.zone_occupancy[current] -= 1
        self.zone_occupancy[next_node] += 1

        drone.position = next_node

        return next_node

    # -------------------------
    def run(self):

        self.plan_paths()
        self.rebuild_occupancy()

        while not self.all_finished():
            self.save_frame()

            self.turn += 1

            # print(Fore.CYAN + f"\n===== TURN {self.turn} =====")

            edge_reservation = defaultdict(int)

            self.rebuild_occupancy()

            turn_moves = []

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

                if self.can_move(drone, nxt, edge_reservation):
                    next_node = self.move_drone(drone, nxt, edge_reservation)
                    turn_moves.append(f"D{drone.id}-{next_node}")
                    if drone.position == drone.goal:
                        drone.finished = True

            if turn_moves:
                print(Fore.YELLOW + " ".join(turn_moves))
        self.save_frame()

    def save_frame(self):
        frame = {}

        for drone in self.drones:
            frame[str(drone.id)] = drone.position

        self.frames.append(frame)
