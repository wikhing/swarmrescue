from mesa import Agent, Model
from mesa.space import MultiGrid

class DroneAgent(Agent):
    def __init__(self, model):
        super().__init__(model) 
        self.battery = 100

    def step(self):
        # Communication: Mark current position as searched
        self.model.visited_cells.add(self.pos)

        # Look at surrounding squares
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True, # allows diagonally movement
            include_center=False
        )

        # Filter out squares the swarm has already searched
        unvisited_steps = [step for step in possible_steps if step not in self.model.visited_cells]

        if unvisited_steps:
            # Pick the unvisited square FURTHEST from other drones
            best_step = None
            max_distance = -1

            # Find all other drones to coordinate with
            other_drones = [agent for agent in self.model.agents if isinstance(agent, DroneAgent) and agent != self]

            for step in unvisited_steps:
                # Calculate "Manhattan distance" to other drones
                dist_to_others = 0
                for other in other_drones:
                    dist_to_others += (abs(step[0] - other.pos[0]) + abs(step[1] - other.pos[1]))

                if dist_to_others > max_distance:
                    max_distance = dist_to_others
                    best_step = step
            
            new_position = best_step
        else:
            # If completely surrounded by searched squares, move randomly to break out
            new_position = self.random.choice(possible_steps)

        # Execute the move and update the shared map
        self.model.grid.move_agent(self, new_position)
        self.model.visited_cells.add(new_position)

class SurvivorAgent(Agent):
    def __init__(self, model):
        super().__init__(model)
    def step(self):
        pass

class RescueModel(Model):
    def __init__(self, width=10, height=10, num_drones=3):
        super().__init__()
        self.running = True 
        
        # Shared the memory map for each other
        self.visited_cells = set() 
        
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
        
        # Stop the simulation if a drone finds survivor
        cell_contents = self.grid.get_cell_list_contents([self.survivor_location])
        has_drone = any(isinstance(obj, DroneAgent) for obj in cell_contents)
        
        if has_drone:
            print("\n[UI SYSTEM] Survivor found! Halting swarm search.")
            self.running = False