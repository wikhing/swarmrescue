import json
import os
import time
from fastmcp import FastMCP
from simulation import RescueModel, VisitedMarker

mcp = FastMCP("RescueSwarm")
sim = RescueModel(width=15, height=15, num_drones=4, num_survivors=1)

def save_state(log_msg=""):
    """Dumps the grid coordinates and terminal logs to JSON Data Bridge."""
    state = {"drones": [], "survivors": [], "markers": [], "logs": []}
    
    if os.path.exists("swarm_state.json"):
        try:
            with open("swarm_state.json", "r") as f:
                old_state = json.load(f)
                state["logs"] = old_state.get("logs", [])
        except: pass
    
    if log_msg:
        state["logs"].append(log_msg)
        state["logs"] = state["logs"][-15:] 
        
    drones = sorted([a for a in sim.agents if type(a).__name__ == "DroneAgent"], key=lambda x: x.unique_id)
    for a in drones:
        state["drones"].append({"pos": a.pos, "battery": a.battery})
        
    survivors = sorted([a for a in sim.agents if type(a).__name__ == "SurvivorAgent"], key=lambda x: x.unique_id)
    for a in survivors:
        state["survivors"].append({"pos": a.pos})
        
    for a in sim.agents:
        if type(a).__name__ == "VisitedMarker":
            state["markers"].append({"pos": a.pos})
            
    with open("swarm_state.json", "w") as f:
        json.dump(state, f)

save_state("[SYSTEM] MCP Server Online. Awaiting Swarm Commander AI...")

@mcp.tool()
def get_mission_brief() -> str:
    """Returns grid boundaries, charging station location, and discovers active drones (ID, location, battery)."""
    res = f"--- MISSION BRIEF ---\n"
    res += f"Grid Size: X: 0 to {sim.grid.width-1}, Y: 0 to {sim.grid.height-1}\n"
    res += f"Base Station (Recharge Point): {sim.charging_station.pos}\n"
    res += "Active Drones Discovered on Network:\n"
    for a in sim.agents:
        if type(a).__name__ == "DroneAgent":
            res += f"- Drone {a.unique_id} | Pos: {a.pos} | Battery: {a.battery}%\n"
    save_state("[SYSTEM] Swarm Commander downloaded the Mission Brief.")
    return res

@mcp.tool()
def get_distress_signals() -> str:
    """Scans the map for distress signatures and returns coordinates."""
    survivors = [a for a in sim.agents if type(a).__name__ == "SurvivorAgent"]
    if survivors: 
        save_state(f"[SYSTEM] Radar sweep isolated distress signal at {survivors[0].pos}")
        return f"Signal isolated at: {survivors[0].pos}"
    return "No signals found."

@mcp.tool()
def move_drone(drone_id: int, target_x: int, target_y: int) -> str:
    """Moves a drone. Costs 2% battery per grid step distance."""
    for drone in sim.agents:
        if type(drone).__name__ == "DroneAgent" and drone.unique_id == drone_id:
            dist = max(abs(drone.pos[0] - target_x), abs(drone.pos[1] - target_y))
            battery_cost = dist * 2

            if drone.battery < battery_cost:
                return f"ERROR: Drone {drone_id} has {drone.battery}%. Needs {battery_cost}%."

            old_pos = drone.pos
            sim.grid.move_agent(drone, (target_x, target_y))
            drone.battery -= battery_cost

            if old_pos not in sim.visited_cells:
                sim.visited_cells.add(old_pos)
                marker = VisitedMarker(sim)
                sim.grid.place_agent(marker, old_pos)

            save_state(f"[MCP SYSTEM] Drone {drone_id} executed flight to ({target_x}, {target_y}).")
            
            time.sleep(2) 
            
            return f"SUCCESS: Drone {drone_id} moved to ({target_x}, {target_y}). Battery: {drone.battery}%."
    return f"ERROR: Drone {drone_id} not found."

@mcp.tool()
def recharge_drone(drone_id: int) -> str:
    """Recharges drone to 100%. Drone MUST be physically located at the Base Station coordinate to work."""
    for drone in sim.agents:
        if type(drone).__name__ == "DroneAgent" and drone.unique_id == drone_id:
            if drone.pos == sim.charging_station.pos:
                drone.battery = 100
                save_state(f"[MCP SYSTEM] Drone {drone_id} successfully recharged to 100%.")
                time.sleep(1)
                return f"SUCCESS: Drone {drone_id} fully recharged to 100%."
            else:
                return f"ERROR: Drone {drone_id} is not at Base Station. Move it there first."
    return "ERROR: Drone not found."

@mcp.tool()
def thermal_scan(drone_id: int) -> str:
    """Scans current location for survivors. Costs 5% battery."""
    for drone in sim.agents:
        if type(drone).__name__ == "DroneAgent" and drone.unique_id == drone_id:
            drone.battery -= 5
            contents = sim.grid.get_cell_list_contents([drone.pos])
            if any(type(o).__name__ == "SurvivorAgent" for o in contents):
                save_state(f"[MCP SYSTEM] 🚨 SURVIVOR RESCUED BY DRONE {drone_id}! 🚨")
                time.sleep(2)
                return f"CRITICAL SUCCESS: Survivor found at {drone.pos} by Drone {drone_id}!"
            
            save_state(f"[MCP SYSTEM] Drone {drone_id} ran thermal scan. Target empty.")
            return f"No survivor at {drone.pos}."
    return "ERROR: Drone not found."

if __name__ == "__main__":
    mcp.run()