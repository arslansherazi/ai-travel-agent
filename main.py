import os

from agents import Runner, InputGuardrailTripwireTriggered
from agents.mcp import MCPServerSse
from dotenv import load_dotenv
import panel as pn

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
        async with (
            MCPServerSse(name="Booking", params={"url": os.getenv("BOOKING_SERVER_URL")}) as booking_server,
            MCPServerSse(name="Places", params={"url": os.getenv("PLACES_SERVER_URL")}) as places_server,
            MCPServerSse(name="Planner", params={"url": os.getenv("PLANNER_SERVER_URL")}) as planner_server,
            MCPServerSse(name="Weather", params={"url": os.getenv("WEATHER_SERVER_URL")}) as weather_server
        ):
            # Setup servers for all agents
            booking_agent.server = booking_server
            places_agent.server = places_server
            planner_agent.server = planner_server
            weather_agent.server = weather_server

            # Simple routing logic - start with weather agent for weather queries
            weather_keywords = ['weather', 'temperature', 'forecast', 'rain', 'snow', 'sunny', 'cloudy']
            if any(keyword in _input.lower() for keyword in weather_keywords):
                result = await Runner.run(starting_agent=weather_agent, input=_input)
            else:
                # Use controller for other queries
                controller_agent.handoffs = [weather_agent, booking_agent, places_agent, planner_agent]
                result = await Runner.run(starting_agent=controller_agent, input=_input)
            
            return result.final_output
    except InputGuardrailTripwireTriggered:
        return "I'm sorry, I can only assist with travel‑related questions. Please ask me about weather, accommodations, places, or trip planning."
    except Exception as e:
        return f"Something went wrong. Please try again with a different request. Error: {str(e)}"
def run():
    """
    Run the application with Panel UI
    """
    pn.extension()

    # Create the chat interface
    chat_interface = pn.chat.ChatInterface(
        callback=process_user_query,
        callback_user="Travel Assistant",
        show_rerun=False,
        show_undo=False,
        show_clear=True
    )

    # Add a welcome message
    chat_interface.send(
        "Welcome to the AI Travel Assistant! How can I help with your travel needs?", 
        user="Travel Assistant", 
        respond=False
    )

    # Create the app layout
    app = pn.Column(
        pn.pane.Markdown("# 🌍 AI Travel Assistant", align="center"),
        chat_interface,
        width=800,
        sizing_mode="stretch_width"
    )

    # Serve the app
    app.servable("Travel Assistant")
    pn.serve(app, port=5006, show=True)


if __name__ == "__main__":
    run()