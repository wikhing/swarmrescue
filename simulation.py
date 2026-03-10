from mesa import Agent, Model
from mesa.space import MultiGrid

class DroneAgent(Agent):
    def __init__(self, model):
        super().__init__(model) 
        self.battery = 100

    def step(self):
        # Random search pattern: Move to a random adjacent cell each turn
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True, # allows diagonally movement
            include_center=False
        )
        # Pick a random square next to the drone and move there
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

class SurvivorAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
    def step(self):
        pass

class RescueModel(Model):
    def __init__(self, width=10, height=10, num_drones=3):
        super().__init__()
        self.num_drones = num_drones
        self.grid = MultiGrid(width, height, True)
        self.survivor_location = (8, 2)

        # Place the Survivor
        self.survivor = SurvivorAgent(self)
        self.grid.place_agent(self.survivor, self.survivor_location)

        # Place the Drones
        for _ in range(self.num_drones):
            drone = DroneAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(drone, (x, y))

    def step(self):
        self.agents.shuffle_do("step")