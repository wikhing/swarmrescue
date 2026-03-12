from mesa.visualization import SolaraViz, make_space_component
from simulation import RescueModel

def agent_portrayal(agent):
    if type(agent).__name__ == "DroneAgent":
        return {"color": "tab:blue", "marker": "o", "size": 150}
    elif type(agent).__name__ == "SurvivorAgent":
        return {"color": "tab:red", "marker": "*", "size": 200}
    elif type(agent).__name__ == "VisitedMarker":
        return {"color": "lightgreen", "marker": "s", "size": 50}
    return {}

space = make_space_component(agent_portrayal)

model_params = {
    "width": 10,
    "height": 10,
    "num_drones": 3
}

starter_model = RescueModel(width=10, height=10, num_drones=3)

page = SolaraViz(
    starter_model, 
    components=[space],
    model_params=model_params,
    name="Swarm Rescue Live Radar"
)