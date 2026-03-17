import json
import os
from mesa import Agent, Model
from mesa.space import MultiGrid

class VisitedMarker(Agent):
    def __init__(self, model): super().__init__(model)
    def step(self): pass

class ChargingStationAgent(Agent):
    def __init__(self, model): super().__init__(model)
    def step(self): pass

class SurvivorAgent(Agent):
    def __init__(self, model): super().__init__(model)
    def step(self): pass

class DroneAgent(Agent):
    def __init__(self, model): 
        super().__init__(model) 
        self.battery = self.model.random.choice([25, 45, 80, 100]) 
    def step(self): pass 

class RescueModel(Model):
    def __init__(self, width=15, height=15, num_drones=4, num_survivors=1, **kwargs):
        super().__init__(**kwargs) 
        self.running = True 
        self.visited_cells = set() 
        self.num_drones = num_drones
        self.num_survivors = num_survivors
        self.grid = MultiGrid(width, height, False)

        self.charging_station = ChargingStationAgent(self)
        self.grid.place_agent(self.charging_station, (width//2, height//2))

        for _ in range(self.num_survivors):
            survivor = SurvivorAgent(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(survivor, (x, y))

        for _ in range(self.num_drones):
            drone = DroneAgent(self)
            self.grid.place_agent(drone, (width//2, height//2))

    def step(self):
        if os.path.exists("swarm_state.json"):
            try:
                with open("swarm_state.json", "r") as f:
                    state = json.load(f)
                
                ui_drones = sorted([a for a in self.agents if type(a).__name__ == "DroneAgent"], key=lambda d: d.unique_id)
                for i, d_data in enumerate(state.get("drones", [])):
                    if i < len(ui_drones):
                        self.grid.move_agent(ui_drones[i], tuple(d_data["pos"]))
                        ui_drones[i].battery = d_data["battery"]

                ui_survivors = sorted([a for a in self.agents if type(a).__name__ == "SurvivorAgent"], key=lambda s: s.unique_id)
                for i, s_data in enumerate(state.get("survivors", [])):
                    if i < len(ui_survivors):
                        self.grid.move_agent(ui_survivors[i], tuple(s_data["pos"]))
                        
                ui_markers = [a for a in self.agents if type(a).__name__ == "VisitedMarker"]
                state_markers = state.get("markers", [])
                if len(state_markers) > len(ui_markers):
                    for m_data in state_markers[len(ui_markers):]:
                        marker = VisitedMarker(self)
                        self.grid.place_agent(marker, tuple(m_data["pos"]))
                        
            except Exception as e:
                print(f"Data Bridge Error: {e}")

        self.agents.shuffle_do("step")