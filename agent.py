import os
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def run_mission():
    server_params = StdioServerParameters(command="python", args=["mcp_server.py"], env=os.environ)
    
    with MCPServerAdapter(server_params) as tools:
        
        swarm_commander = Agent(
            role="Swarm Commander AI",
            goal="Coordinate a fleet of drones, strictly manage battery constraints, and rescue survivors.",
            backstory="""You are a strictly logical AI. 
            CRITICAL JUDGING RUBRIC RULES:
            1. REAL-TIME DISCOVERY: Use `get_mission_brief` to discover active drones. NEVER guess their IDs.
            2. STRATEGIC MANAGEMENT: You must assign different drones to different tasks based on their battery.
            3. MANDATORY PROTOCOL: You must use the MCP `move_drone` and `recharge_drone` tools.
            4. CHAIN OF THOUGHT: Before executing any move, you MUST explain your logic using this exact format:
               "Drone [ID] has [X]% battery, so I am assigning the closer Sector [Y] to it while sending Drone [ID2] to the further Sector [Z]"
            """,
            tools=tools,
            llm="gemini/gemini-2.5-flash",
            verbose=True,
            max_rpm=15,
            max_iter=10
        )
        
        mission_task = Task(
            description="""
            Execute the following operational sequence to prove system capabilities:
            1. Use `get_mission_brief` to map the grid, locate the base station, and check drone batteries.
            2. Use `get_distress_signals` to find the target.
            3. Analyze the fleet: 
               - Pick ONE drone with high battery and send it to the distress signal.
               - Pick ONE drone with LOW battery, keep it at (or send it to) the Base Station coordinate, and use the `recharge_drone` tool on it to prove you can manage resources.
            4. Once the rescue drone reaches the target, use `thermal_scan`.
            """,
            expected_output="A full operational log showing real-time tool discovery, Chain-of-Thought resource allocation, and a successful thermal scan.",
            agent=swarm_commander
        )
        
        crew = Crew(agents=[swarm_commander], tasks=[mission_task], verbose=True)
        print("\n🚨 INITIATING SWARM COMMAND VIA MCP... 🚨\n" + "-"*60)
        result = crew.kickoff()
        print("\n" + "="*60 + "\nFINAL MISSION LOG:\n" + str(result))

if __name__ == "__main__":
    run_mission()