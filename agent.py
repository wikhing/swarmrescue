import os
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

def run_mission():
    print("Initiating First Responder Swarm Interface...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=os.environ
    )
    
    with MCPServerAdapter(server_params) as tools:
        
        # The Agents
        radar_agent = Agent(
            role="Radar Specialist",
            goal="Monitor the disaster zone and report exactly which drones are active and their battery levels.",
            backstory="You are an expert at analyzing drone telemetry. You never guess; you always use your tools to check the exact status of the swarm.",
            tools=tools,
            llm="gemini/gemini-2.5-flash",
            verbose=True
        )
        
        pilot_agent = Agent(
            role="Rescue Pilot",
            goal="Move drones to requested coordinates, manage battery life, and scan for survivors.",
            backstory="""You are a veteran drone pilot. 
            CRITICAL RULES: 
            1. Before moving, you MUST explain your reasoning about the battery level.
            2. Moving costs 10% battery. Scanning costs 5% battery.
            3. If a drone's battery is below 20%, you MUST use the recharge_drone tool before using it.
            4. Always use the thermal_scan tool after arriving at a destination.""",
            tools=tools,
            llm="gemini/gemini-2.5-flash",
            verbose=True
        )
        
        # The Tasks
        scan_task = Task(
            description="Use the get_active_drones tool to get the list of active drones and their battery levels. Pass this data to the pilot.",
            expected_output="A list of active drones and their current battery levels.",
            agent=radar_agent
        )
        
        rescue_task = Task(
            description="""We received a faint distress signal from Sector 8-2 (Coordinate X:8, Y:2). 
            Look at the active drones list. Pick a drone with a high battery level.
            First, move that drone to X:8, Y:2. 
            Second, execute a thermal_scan with that drone to find the survivor.""",
            expected_output="Confirmation of the thermal scan results at coordinate (8, 2).",
            agent=pilot_agent
        )
        
        # The Crew
        rescue_swarm = Crew(
            agents=[radar_agent, pilot_agent],
            tasks=[scan_task, rescue_task],
            verbose=True
        )
        
        print("\n🚨 URGENT MISSION: Distress signal detected at (8, 2). Dispatching Swarm. 🚨\n" + "-"*60)
        
        result = rescue_swarm.kickoff()
        
        print("\n" + "="*60)
        print("FINAL MISSION LOG FOR JUDGES:")
        print(result)

if __name__ == "__main__":
    run_mission()