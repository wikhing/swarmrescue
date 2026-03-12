from mesa.visualization import SolaraViz, make_space_component
from simulation import RescueModel

def agent_portrayal(agent):
    name = type(agent).__name__
    
    if name == "DroneAgent":
        return {"color": "tab:blue", "marker": "o", "size": 150}
    elif name == "SurvivorAgent":
        return {"color": "tab:red", "marker": "*", "size": 200}
    elif name == "VisitedMarker":
        return {"color": "lightgreen", "marker": "s", "size": 50}
    return {}

space = make_space_component(agent_portrayal)

model_params = {
    "width": {
        "type": "SliderInt",
        "value": 15,
        "label": "Grid Width",
        "min": 10,  # Minimum grid size
        "max": 30,  # Maximum grid size
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 15,
        "label": "Grid Height",
        "min": 10,
        "max": 30,
        "step": 1,
    },
    "num_drones": {
        "type": "SliderInt",
        "value": 4,
        "label": "Number of Drones",
        "min": 1,
        "max": 15,
        "step": 1,
    },
    "num_survivors": {
        "type": "SliderInt",
        "value": 1,
        "label": "Number of Survivors",
        "min": 1,
        "max": 10,
        "step": 1,
    }
}

starter_model = RescueModel(width=15, height=15, num_drones=4, num_survivors=1)

page = SolaraViz(
    starter_model, 
    components=[space],
    model_params=model_params,
    name="Swarm Rescue Live Radar"
)