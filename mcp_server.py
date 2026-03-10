from fastmcp import FastMCP
from simulation import RescueModel, DroneAgent

mcp = FastMCP("RescueSwarm")
sim = RescueModel(width=10, height=10, num_drones=3)

@mcp.tool()
def get_active_drones() -> str:
    """Returns a list of all active drones, their exact X/Y locations, and their battery levels."""
    status_list = []
    print("\n[SYSTEM] Radar Specialist requested drone status.")
    
    for drone in sim.agents:
        if isinstance(drone, DroneAgent):
            status = f"Drone {drone.unique_id}: Location {drone.pos}, Battery {drone.battery}%"
            status_list.append(status)
    return "\n".join(status_list)

@mcp.tool()
def move_drone(drone_id: int, x: int, y: int) -> str:
    """Moves a specific drone by its ID to a new X, Y coordinate. Uses 10% battery."""
    for drone in sim.agents:
        if isinstance(drone, DroneAgent) and drone.unique_id == drone_id:
            if drone.battery <= 10:
                return f"ALERT: Drone {drone_id} battery critically low! Must recharge."
            
            sim.grid.move_agent(drone, (x, y))
            drone.battery -= 10
            
            print(f"\n[SYSTEM] Drone {drone_id} moved to ({x}, {y})")
            
            return f"Success: Drone {drone_id} flew to ({x}, {y}). Battery is now {drone.battery}%."
            
    return f"Error: Could not find Drone {drone_id}."

@mcp.tool()
def thermal_scan(drone_id: int) -> str:
    """Scans the drone's current grid location for thermal signatures (survivors). Uses 5% battery."""
    for drone in sim.agents:
        if isinstance(drone, DroneAgent) and drone.unique_id == drone_id:
            if drone.battery <= 5:
                return f"ALERT: Drone {drone_id} battery too low to scan!"
            
            drone.battery -= 5
            print(f"\n[SYSTEM] Drone {drone_id} is running a thermal scan at {drone.pos}...")
            
            if drone.pos == sim.survivor_location:
                return f"CRITICAL SUCCESS! Drone {drone_id} found a survivor at {drone.pos}!"
            else:
                return f"Scan complete at {drone.pos}. No survivors found. Battery: {drone.battery}%."
                
    return f"Error: Could not find Drone {drone_id}."

@mcp.tool()
def recharge_drone(drone_id: int) -> str:
    """Recharges a drone back to 100% battery."""
    for drone in sim.agents:
        if isinstance(drone, DroneAgent) and drone.unique_id == drone_id:
            drone.battery = 100
            print(f"\n[SYSTEM] Drone {drone_id} recharged to 100%.")
            return f"Drone {drone_id} has been fully recharged to 100%."
    return f"Error: Could not find Drone {drone_id}."

if __name__ == "__main__":
    mcp.run()