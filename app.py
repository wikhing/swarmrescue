import solara
import json
import os
import time
import threading
from mesa.visualization import SolaraViz, make_space_component
from simulation import RescueModel

def agent_portrayal(agent):
    name = type(agent).__name__
    if name == "DroneAgent": return {"color": "tab:blue", "marker": "o", "size": 150}
    elif name == "SurvivorAgent": return {"color": "tab:red", "marker": "*", "size": 200}
    elif name == "VisitedMarker": return {"color": "lightgreen", "marker": "s", "size": 50}
    elif name == "ChargingStationAgent": return {"color": "gold", "marker": "s", "size": 250} 
    return {}

space = make_space_component(agent_portrayal)

model_params = {
    "width": { "type": "SliderInt", "value": 15, "label": "Grid Width", "min": 10, "max": 30, "step": 1 },
    "height": { "type": "SliderInt", "value": 15, "label": "Grid Height", "min": 10, "max": 30, "step": 1 },
    "num_drones": { "type": "SliderInt", "value": 4, "label": "Number of Drones", "min": 1, "max": 15, "step": 1 },
    "num_survivors": { "type": "SliderInt", "value": 1, "label": "Number of Survivors", "min": 1, "max": 10, "step": 1 }
}

starter_model = RescueModel(width=15, height=15, num_drones=4, num_survivors=1)

@solara.component
def MCPServerLogs():
    logs, set_logs = solara.use_state(["[WAITING] Awaiting MCP Connection..."])

    def start_polling():
        active = True
        
        def poll():
            while active:
                if os.path.exists("swarm_state.json"):
                    try:
                        with open("swarm_state.json", "r") as f:
                            data = json.load(f)
                            set_logs(data.get("logs", ["[WAITING] Awaiting MCP Connection..."]))
                    except Exception:
                        pass
                time.sleep(1)
                
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()

        def cleanup():
            nonlocal active
            active = False
        return cleanup

    solara.use_effect(start_polling, [])

    with solara.Card(title="📡 Live Swarm Telemetry", style={"max-width": "800px", "margin": "auto", "margin-top": "20px"}):
        with solara.Column(style={"background-color": "#1e1e1e", "color": "#00ff00", "padding": "15px", "border-radius": "5px", "font-family": "monospace", "height": "250px", "overflow-y": "auto"}):
            for log in logs:
                solara.Text(log)

@solara.component
def Page():
    with solara.Column():
        SolaraViz(
            starter_model, 
            components=[space],
            model_params=model_params,
            name="Swarm Rescue Live Radar"
        )
        MCPServerLogs()

page = Page