import os

from agents import Runner, InputGuardrailTripwireTriggered, trace
from agents.mcp import MCPServerSse
from dotenv import load_dotenv

from _agents.booking import booking_agent
from _agents.controller import controller_agent
from _agents.places import places_agent
from _agents.planner import planner_agent
from _agents.weather import weather_agent

load_dotenv()


async def process_user_query(_input: str):
    """
    Processes user query and fetch the response from agents

    :param _input: User query string
    """
    try:
        # Get server URLs with defaults
        booking_url = os.getenv("BOOKING_SERVER_URL", "http://localhost:8001")
        places_url = os.getenv("PLACES_SERVER_URL", "http://localhost:8002")
        planner_url = os.getenv("PLANNER_SERVER_URL", "http://localhost:8003")
        weather_url = os.getenv("WEATHER_SERVER_URL", "http://localhost:8004")

        with trace("AI Travel Assistant Workflow"):
            async with (
                MCPServerSse(name="Booking", params={"url": booking_url}) as booking_server,
                MCPServerSse(name="Places", params={"url": places_url}) as places_server,
                MCPServerSse(name="Planner", params={"url": planner_url}) as planner_server,
                MCPServerSse(name="Weather", params={"url": weather_url}) as weather_server
            ):
                # Connect agents to their respective MCP servers (using mcp_servers list)
                booking_agent.mcp_servers = [booking_server]
                places_agent.mcp_servers = [places_server]
                planner_agent.mcp_servers = [planner_server]
                weather_agent.mcp_servers = [weather_server]

                # Setup handoffs between agents
                controller_agent.handoffs = [weather_agent, booking_agent, places_agent, planner_agent]
                weather_agent.handoffs = [controller_agent]
                booking_agent.handoffs = [controller_agent]
                places_agent.handoffs = [controller_agent]
                planner_agent.handoffs = [controller_agent]

                # Run with session for automatic conversation memory
                result = await Runner.run(
                    starting_agent=controller_agent,
                    input=_input
                )

                return result.final_output

    except InputGuardrailTripwireTriggered as e:
        print(f"Guardrail blocked this input: {e}")
        return "I can only help with travel-related questions and greetings. Please ask about weather, accommodations, places to visit, or trip planning."
    except Exception as e:
        print(f"Error processing query: {e}")
        return "I encountered an error while processing your request. Please try again."
