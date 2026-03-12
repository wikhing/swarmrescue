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
            goal="Monitor the disaster zone, find distress signals, and report active drones.",
            backstory="You are an expert at analyzing drone telemetry. You never guess; you always use your tools.",
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
            description="Use get_active_drones to get drone status. THEN use get_distress_signal to find the target coordinate. Pass BOTH the drone list and the target coordinate to the pilot.",
            expected_output="A list of active drones and the exact coordinate of the distress signal.",
            agent=radar_agent
        )
        
        rescue_task = Task(
            description="""Look at the data provided by the Radar Specialist. 
            Pick a drone with a high battery level.
            First, move that drone to the distress signal coordinate provided. 
            Second, execute a thermal_scan with that drone to confirm the survivor.""",
            expected_output="Confirmation of the thermal scan results at the target coordinate.",
            agent=pilot_agent
        )
        
        # The Crew
        rescue_swarm = Crew(
            agents=[radar_agent, pilot_agent],
            tasks=[scan_task, rescue_task],
            verbose=True
        )
        
        print("\n🚨 URGENT MISSION: Scanning for distress signals. Dispatching Swarm. 🚨\n" + "-"*60)
        result = rescue_swarm.kickoff()
        print("\n" + "="*60 + "\nFINAL MISSION LOG FOR JUDGES:\n" + str(result))

if __name__ == "__main__":
    run_mission()