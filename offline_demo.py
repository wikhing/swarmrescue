import time
import mcp_server as server

print("\n🚨 INITIATING OFFLINE AI DEMO OVERRIDE 🚨\n" + "="*50)
time.sleep(2)

print("\n[AI THOUGHT] Booting up and requesting mission brief...")
print(server.get_mission_brief())
time.sleep(2)

print("\n[AI THOUGHT] Scanning for distress signals...")
target_msg = server.get_distress_signals()
print(target_msg)
time.sleep(2)

# Extract the target coordinates from the message dynamically
import ast
coord_str = target_msg.split("at: ")[1]
target_x, target_y = ast.literal_eval(coord_str)

# Find the IDs of the drones dynamically
drones = [a for a in server.sim.agents if type(a).__name__ == "DroneAgent"]
rescue_drone_id = drones[0].unique_id
recharge_drone_id = drones[1].unique_id

print(f"\n[AI THOUGHT] Analysis complete. Drone {rescue_drone_id} has high battery. Dispatching to ({target_x}, {target_y}).")
print(f"[AI THOUGHT] Drone {recharge_drone_id} requires charging. Ordering it to remain at base.")
time.sleep(2)

# --- EXECUTE MOVES ---
print(server.move_drone(rescue_drone_id, target_x, target_y))
time.sleep(2)

print("\n[AI THOUGHT] Drone has arrived at target coordinates. Initiating thermal scan...")
print(server.thermal_scan(rescue_drone_id))
time.sleep(2)

print(f"\n[AI THOUGHT] Commencing recharge protocol for Drone {recharge_drone_id}...")
print(server.recharge_drone(recharge_drone_id))

print("\n" + "="*50 + "\nDEMO SEQUENCE COMPLETE. NO API QUOTA USED.")