from mesa import Agent, Model
from mesa.space import MultiGrid

class VisitedMarker(Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        pass

class DroneAgent(Agent):
    def __init__(self, model):
        super().__init__(model) 
        self.battery = 100

    def step(self):
        old_position = self.pos
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        unvisited_steps = [step for step in possible_steps if step not in self.model.visited_cells]

        if unvisited_steps:
            best_step = None
            max_distance = -1
            other_drones = [a for a in self.model.agents if type(a).__name__ == "DroneAgent" and a != self]

            for step in unvisited_steps:
                dist_to_others = sum(abs(step[0] - other.pos[0]) + abs(step[1] - other.pos[1]) for other in other_drones)
                if dist_to_others > max_distance:
                    max_distance = dist_to_others
                    best_step = step
            new_position = best_step
        else:
            new_position = self.random.choice(possible_steps)

        self.model.grid.move_agent(self, new_position)
        
        if old_position not in self.model.visited_cells:
            self.model.visited_cells.add(old_position)
            marker = VisitedMarker(self.model)
            self.model.grid.place_agent(marker, old_position)

class SurvivorAgent(Agent):
    def __init__(self, model):
        super().__init__(model)

    def step(self):
        pass

class RescueModel(Model):
    def __init__(self, width=15, height=15, num_drones=4, num_survivors=1, **kwargs):
        super().__init__(**kwargs) 
        self.running = True 
        self.visited_cells = set() 
        
        self.num_drones = num_drones
        self.num_survivors = num_survivors
        self.grid = MultiGrid(width, height, True)

        for _ in range(self.num_survivors):
            survivor = SurvivorAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(survivor, (x, y))

        for _ in range(self.num_drones):
            drone = DroneAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(drone, (x, y))

    def step(self):
        self.agents.shuffle_do("step")
        
        survivors = [a for a in self.agents if type(a).__name__ == "SurvivorAgent"]
        for survivor in survivors:
            cell_contents = self.grid.get_cell_list_contents([survivor.pos])
            has_drone = any(type(obj).__name__ == "DroneAgent" for obj in cell_contents)
            
            if has_drone:
                print(f"\n[UI SYSTEM] Survivor found at {survivor.pos}! Halting swarm search.")
                self.running = False 
                break