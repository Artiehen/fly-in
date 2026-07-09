class Drone:

    def __init__(self, drone_id, start, goal):

        self.id = drone_id
        self.position = start
        self.goal = goal
        self.path = []
        self.finished = False
