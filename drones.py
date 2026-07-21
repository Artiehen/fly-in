class Drone:

    def __init__(self, drone_id: int, start: str, goal: str):

        self.id: int = drone_id
        self.position: str = start
        self.goal: str = goal
        self.path: list[str] = []
        self.finished: bool = False
