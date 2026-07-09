import sys

from fileparser import parse_file
from scheduler import Scheduler
from graph import Graph
from drones import Drone
from htmlexporter import HTMLExporter


def create_drones(nb_drones, start, goal):

    return [
        Drone(i + 1, start, goal)
        for i in range(nb_drones)
    ]


# -------------------------
# Find start/end hubs
# -------------------------
def get_start_end(hubs):

    start = None
    end = None

    for hub in hubs.values():

        if hub.kind == "start":
            start = hub.name

        elif hub.kind == "end":
            end = hub.name

    if start is None or end is None:
        raise Exception("Missing start or end hub")

    return start, end


# -------------------------
# MAIN
# -------------------------
def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        return

    filename = sys.argv[1]

    # 1. Parse file
    nb_drones, hubs, connections = parse_file(filename)

    # 2. Find start/end
    start, goal = get_start_end(hubs)

    # 3. Build drones
    drones = create_drones(nb_drones, start, goal)

    # 4. Create scheduler
    graph = Graph(hubs, connections)

    scheduler = Scheduler(
        graph,
        hubs,
        drones
    )

    # 6. Run simulation
    scheduler.run()
    print(f"Total ammount of turns: {scheduler.turn}")
    exporter = HTMLExporter(
        hubs,
        connections,
        scheduler.frames
    )

    exporter.export("simulation.html")


if __name__ == "__main__":
    main()
